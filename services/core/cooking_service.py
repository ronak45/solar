from typing import List, Dict, Optional, Tuple
from uuid import UUID
from solar.access import public
from solar.media import MediaFile, save_to_bucket, generate_presigned_url
from openai import OpenAI
import os
import json
from datetime import datetime
from core.cooking_session import CookingSession
from core.base_recipe import BaseRecipe
from core.nutrition_data import NutritionData

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@public
def start_cooking_session(user_id: str, base_recipe_id: UUID) -> CookingSession:
    """Start a new cooking session for a recipe."""
    # Get the base recipe
    recipe_results = BaseRecipe.sql(
        "SELECT * FROM base_recipes WHERE id = %(recipe_id)s",
        {"recipe_id": str(base_recipe_id)}
    )
    
    if not recipe_results:
        raise ValueError(f"Recipe {base_recipe_id} not found")
    
    recipe = BaseRecipe(**recipe_results[0])
    
    session = CookingSession(
        user_id=user_id,
        base_recipe_id=base_recipe_id,
        status="in_progress",
        decisions_made=[],
        current_step=1,
        final_ingredients=recipe.base_ingredients.copy(),
        final_steps=recipe.base_steps.copy(),
        final_nutrition=recipe.base_nutrition.copy(),
        final_cost=recipe.base_cost_estimate,
        total_time_minutes=recipe.prep_time_minutes + recipe.cook_time_minutes,
        session_photos=[],
        voice_interactions=[]
    )
    session.sync()
    
    return session

@public
def make_cooking_decision(session_id: UUID, branch_point: int, choice: str) -> Dict:
    """Make a decision at a branching point and update the recipe accordingly."""
    # Get the session
    session_results = CookingSession.sql(
        "SELECT * FROM cooking_sessions WHERE id = %(session_id)s",
        {"session_id": str(session_id)}
    )
    
    if not session_results:
        raise ValueError(f"Cooking session {session_id} not found")
    
    session = CookingSession(**session_results[0])
    
    # Get the base recipe
    recipe_results = BaseRecipe.sql(
        "SELECT * FROM base_recipes WHERE id = %(recipe_id)s",
        {"recipe_id": str(session.base_recipe_id)}
    )
    
    recipe = BaseRecipe(**recipe_results[0])
    
    # Find the branch point
    branch_info = None
    for bp in recipe.branch_points:
        if bp["step"] == branch_point:
            branch_info = bp
            break
    
    if not branch_info:
        raise ValueError(f"Branch point {branch_point} not found")
    
    # Record the decision
    decision = {
        "branch_point": branch_point,
        "choice": choice,
        "timestamp": datetime.now().isoformat()
    }
    session.decisions_made.append(decision)
    
    # Use LLM to recompose the recipe based on the decision
    updated_recipe = recompose_recipe_with_decision(
        recipe, session.final_ingredients, session.final_steps, 
        branch_info, choice
    )
    
    # Update session with new recipe state
    session.final_ingredients = updated_recipe["ingredients"]
    session.final_steps = updated_recipe["steps"]
    session.final_nutrition = updated_recipe["nutrition"]
    session.final_cost = updated_recipe["cost"]
    session.total_time_minutes = updated_recipe["total_time"]
    session.sync()
    
    return {
        "session": session,
        "updated_recipe": updated_recipe,
        "next_branch_points": get_upcoming_branch_points(recipe, session.current_step + 1)
    }

@public
def process_voice_question(session_id: UUID, question: str) -> Dict:
    """Process a voice question during cooking and provide guidance."""
    # Get the session
    session_results = CookingSession.sql(
        "SELECT * FROM cooking_sessions WHERE id = %(session_id)s",
        {"session_id": str(session_id)}
    )
    
    if not session_results:
        raise ValueError(f"Cooking session {session_id} not found")
    
    session = CookingSession(**session_results[0])
    
    # Generate response using current recipe context
    response = client.chat.completions.create(
        model="openai/o4-mini",
        messages=[
            {"role": "system", "content": f"""You are a helpful cooking assistant. The user is currently cooking and has asked a question.
            
            Current recipe state:
            - Ingredients: {json.dumps(session.final_ingredients)}
            - Current step: {session.current_step}
            - Steps: {json.dumps(session.final_steps)}
            
            Answer their cooking question helpfully and concisely. If they're asking about ingredient substitutions, 
            consider if it would create a significant branch in the recipe that should be recorded."""},
            {"role": "user", "content": question}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "cooking_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string"},
                        "creates_branch": {"type": "boolean"},
                        "suggested_modification": {"type": ["string", "null"]}
                    },
                    "required": ["answer", "creates_branch", "suggested_modification"],
                    "additionalProperties": False
                }
            }
        }
    )
    
    result = json.loads(response.choices[0].message.content)
    
    # Record the voice interaction
    interaction = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "response": result["answer"]
    }
    session.voice_interactions.append(interaction)
    session.sync()
    
    return result

@public
def add_cooking_photo(session_id: UUID, photo: MediaFile, step_number: int) -> str:
    """Add a photo taken during cooking."""
    # Save the photo
    photo_path = save_to_bucket(photo)
    
    # Get and update the session
    session_results = CookingSession.sql(
        "SELECT * FROM cooking_sessions WHERE id = %(session_id)s",
        {"session_id": str(session_id)}
    )
    
    if not session_results:
        raise ValueError(f"Cooking session {session_id} not found")
    
    session = CookingSession(**session_results[0])
    session.session_photos.append(photo_path)
    session.sync()
    
    # Return presigned URL for immediate use
    return generate_presigned_url(photo_path)

@public
def update_current_step(session_id: UUID, step_number: int) -> CookingSession:
    """Update the current step in the cooking process."""
    session_results = CookingSession.sql(
        "SELECT * FROM cooking_sessions WHERE id = %(session_id)s",
        {"session_id": str(session_id)}
    )
    
    if not session_results:
        raise ValueError(f"Cooking session {session_id} not found")
    
    session = CookingSession(**session_results[0])
    session.current_step = step_number
    session.sync()
    
    return session

@public
def complete_cooking_session(session_id: UUID, rating: Optional[int] = None, 
                           notes: Optional[str] = None, would_make_again: Optional[bool] = None) -> Dict:
    """Complete a cooking session and generate the story summary."""
    session_results = CookingSession.sql(
        "SELECT * FROM cooking_sessions WHERE id = %(session_id)s",
        {"session_id": str(session_id)}
    )
    
    if not session_results:
        raise ValueError(f"Cooking session {session_id} not found")
    
    session = CookingSession(**session_results[0])
    session.status = "completed"
    session.completed_at = datetime.now()
    session.rating = rating
    session.notes = notes
    session.would_make_again = would_make_again
    session.sync()
    
    # Generate cooking story
    story = generate_cooking_story(session)
    
    return {
        "session": session,
        "story": story
    }

@public
def get_cooking_session(session_id: UUID) -> Optional[CookingSession]:
    """Get a cooking session by ID."""
    results = CookingSession.sql(
        "SELECT * FROM cooking_sessions WHERE id = %(session_id)s",
        {"session_id": str(session_id)}
    )
    
    if results:
        session = CookingSession(**results[0])
        # Generate presigned URLs for photos
        session.session_photos = [generate_presigned_url(path) for path in session.session_photos]
        return session
    return None

@public
def get_user_cooking_sessions(user_id: str) -> List[CookingSession]:
    """Get all cooking sessions for a user."""
    results = CookingSession.sql(
        "SELECT * FROM cooking_sessions WHERE user_id = %(user_id)s ORDER BY started_at DESC",
        {"user_id": user_id}
    )
    
    sessions = [CookingSession(**result) for result in results]
    
    # Generate presigned URLs for photos
    for session in sessions:
        session.session_photos = [generate_presigned_url(path) for path in session.session_photos]
    
    return sessions

def recompose_recipe_with_decision(recipe: BaseRecipe, current_ingredients: List[Dict], 
                                 current_steps: List[Dict], branch_info: Dict, choice: str) -> Dict:
    """Use LLM to recompose recipe based on a branching decision."""
    response = client.chat.completions.create(
        model="openai/o4-mini",
        messages=[
            {"role": "system", "content": "You are a cooking expert who updates recipes based on user decisions. Recalculate all affected elements."},
            {"role": "user", "content": f"""
            Recipe context:
            - Current ingredients: {json.dumps(current_ingredients)}
            - Current steps: {json.dumps(current_steps)}
            - Branch decision: {branch_info['question']} -> {choice}
            
            Please update the recipe to reflect this choice. Modify ingredients, steps, cooking times, and estimate nutrition changes.
            """}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "recipe_update",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "ingredients": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "unit": {"type": "string"},
                                    "required": {"type": "boolean"}
                                },
                                "required": ["name", "quantity", "unit", "required"],
                                "additionalProperties": False
                            }
                        },
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step": {"type": "number"},
                                    "instruction": {"type": "string"},
                                    "time_minutes": {"type": "number"}
                                },
                                "required": ["step", "instruction", "time_minutes"],
                                "additionalProperties": False
                            }
                        },
                        "nutrition": {
                            "type": "object",
                            "properties": {
                                "calories": {"type": "number"},
                                "protein": {"type": "number"},
                                "carbs": {"type": "number"},
                                "fat": {"type": "number"},
                                "fiber": {"type": "number"},
                                "sugar": {"type": "number"},
                                "sodium": {"type": "number"}
                            },
                            "required": ["calories", "protein", "carbs", "fat", "fiber", "sugar", "sodium"],
                            "additionalProperties": False
                        },
                        "cost": {"type": "number"},
                        "total_time": {"type": "number"}
                    },
                    "required": ["ingredients", "steps", "nutrition", "cost", "total_time"],
                    "additionalProperties": False
                }
            }
        }
    )
    
    return json.loads(response.choices[0].message.content)

def get_upcoming_branch_points(recipe: BaseRecipe, current_step: int) -> List[Dict]:
    """Get upcoming branch points from current step."""
    upcoming = []
    for bp in recipe.branch_points:
        if bp["step"] >= current_step:
            upcoming.append(bp)
    return upcoming

def generate_cooking_story(session: CookingSession) -> Dict:
    """Generate a narrative story of the cooking session."""
    response = client.chat.completions.create(
        model="openai/o4-mini",
        messages=[
            {"role": "system", "content": "You are a creative writer who creates engaging stories about cooking adventures."},
            {"role": "user", "content": f"""
            Create a short, engaging story about this cooking session:
            - Decisions made: {json.dumps(session.decisions_made)}
            - Voice interactions: {json.dumps(session.voice_interactions)}
            - Final result: {json.dumps(session.final_nutrition)}
            - Rating: {session.rating}/5 stars
            
            Make it personal and highlight the choices that made this cooking session unique.
            """}
        ]
    )
    
    return {
        "title": f"Cooking Adventure #{session.id}",
        "story": response.choices[0].message.content,
        "decisions_count": len(session.decisions_made),
        "photos_count": len(session.session_photos),
        "cooking_time": session.total_time_minutes
    }