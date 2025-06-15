from typing import List, Dict, Optional, Tuple
from uuid import UUID
from solar.access import public
from openai import OpenAI
import os
import json
from core.base_recipe import BaseRecipe
from core.pantry_item import PantryItem
from core.nutrition_data import NutritionData

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@public
def get_recipe_recommendations(user_id: str, preferences: Optional[str] = None, 
                              dietary_restrictions: Optional[List[str]] = None) -> List[Dict]:
    """Get recipe recommendations based on user's pantry and preferences."""
    # Get user's pantry items
    pantry_results = PantryItem.sql(
        "SELECT name, category, quantity, unit FROM pantry_items WHERE user_id = %(user_id)s",
        {"user_id": user_id}
    )
    
    pantry_items = [f"{item['name']} ({item['quantity']} {item['unit']})" for item in pantry_results]
    
    # Get available recipes
    recipe_results = BaseRecipe.sql("SELECT * FROM base_recipes ORDER BY created_at DESC LIMIT 20")
    recipes = [BaseRecipe(**result) for result in recipe_results]
    
    recommendations = []
    
    for recipe in recipes:
        # Calculate ingredient match percentage
        match_score = calculate_ingredient_match(pantry_items, recipe.base_ingredients)
        
        # Filter by dietary restrictions if provided
        if dietary_restrictions:
            if not any(tag in recipe.dietary_tags for tag in dietary_restrictions):
                continue
        
        recommendations.append({
            "recipe": recipe,
            "match_percentage": match_score,
            "missing_ingredients": get_missing_ingredients(pantry_items, recipe.base_ingredients)
        })
    
    # Sort by match percentage
    recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    return recommendations[:10]  # Return top 10

@public
def get_recipe_by_id(recipe_id: UUID) -> Optional[BaseRecipe]:
    """Get a specific recipe by its ID."""
    results = BaseRecipe.sql(
        "SELECT * FROM base_recipes WHERE id = %(recipe_id)s",
        {"recipe_id": str(recipe_id)}
    )
    
    if results:
        return BaseRecipe(**results[0])
    return None

@public
def create_base_recipe(name: str, description: str, cuisine_type: str, difficulty_level: str,
                      prep_time_minutes: int, cook_time_minutes: int, servings: int,
                      base_ingredients: List[Dict], base_steps: List[Dict],
                      branch_points: List[Dict], dietary_tags: List[str]) -> BaseRecipe:
    """Create a new base recipe."""
    # Calculate basic nutrition and cost
    base_nutrition = calculate_recipe_nutrition(base_ingredients)
    base_cost = calculate_recipe_cost(base_ingredients)
    
    recipe = BaseRecipe(
        name=name,
        description=description,
        cuisine_type=cuisine_type,
        difficulty_level=difficulty_level,
        prep_time_minutes=prep_time_minutes,
        cook_time_minutes=cook_time_minutes,
        servings=servings,
        base_ingredients=base_ingredients,
        base_steps=base_steps,
        branch_points=branch_points,
        base_nutrition=base_nutrition,
        base_cost_estimate=base_cost,
        dietary_tags=dietary_tags,
        ingredient_categories=list(set([ing.get("category", "other") for ing in base_ingredients])),
        created_by="system"
    )
    recipe.sync()
    
    return recipe

@public
def generate_recipe_from_ingredients(ingredient_list: List[str], cuisine_preference: Optional[str] = None,
                                   dietary_restrictions: Optional[List[str]] = None) -> Dict:
    """Generate a new recipe using AI based on available ingredients."""
    dietary_text = ""
    if dietary_restrictions:
        dietary_text = f" The recipe must be {', '.join(dietary_restrictions)}."
    
    cuisine_text = ""
    if cuisine_preference:
        cuisine_text = f" Make it {cuisine_preference} cuisine style."
    
    prompt = f"""Create a complete recipe using primarily these ingredients: {', '.join(ingredient_list)}.{dietary_text}{cuisine_text}
    
    The recipe should include:
    1. A creative name and description
    2. Complete ingredient list with quantities
    3. Step-by-step cooking instructions
    4. 2-3 branching decision points where the cook can make choices that affect the final dish
    5. Estimated prep/cook times and servings
    
    Make it interesting and interactive!"""
    
    response = client.chat.completions.create(
        model="openai/o4-mini",
        messages=[
            {"role": "system", "content": "You are a creative chef who designs interactive cooking experiences with branching choices."},
            {"role": "user", "content": prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "recipe_generation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "cuisine_type": {"type": "string"},
                        "difficulty_level": {"type": "string"},
                        "prep_time_minutes": {"type": "number"},
                        "cook_time_minutes": {"type": "number"},
                        "servings": {"type": "number"},
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
                        "branch_points": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step": {"type": "number"},
                                    "question": {"type": "string"},
                                    "options": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "choice": {"type": "string"},
                                                "description": {"type": "string"}
                                            },
                                            "required": ["choice", "description"],
                                            "additionalProperties": False
                                        }
                                    }
                                },
                                "required": ["step", "question", "options"],
                                "additionalProperties": False
                            }
                        },
                        "dietary_tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["name", "description", "cuisine_type", "difficulty_level", "prep_time_minutes", "cook_time_minutes", "servings", "ingredients", "steps", "branch_points", "dietary_tags"],
                    "additionalProperties": False
                }
            }
        }
    )
    
    return json.loads(response.choices[0].message.content)

def calculate_ingredient_match(pantry_items: List[str], recipe_ingredients: List[Dict]) -> float:
    """Calculate what percentage of recipe ingredients are available in pantry."""
    if not recipe_ingredients:
        return 0.0
    
    pantry_names = [item.split(" (")[0].lower() for item in pantry_items]
    required_ingredients = [ing["name"].lower() for ing in recipe_ingredients if ing.get("required", True)]
    
    if not required_ingredients:
        return 100.0
    
    matched = sum(1 for ing in required_ingredients if any(ing in pantry_name for pantry_name in pantry_names))
    return (matched / len(required_ingredients)) * 100

def get_missing_ingredients(pantry_items: List[str], recipe_ingredients: List[Dict]) -> List[str]:
    """Get list of missing ingredients needed for recipe."""
    pantry_names = [item.split(" (")[0].lower() for item in pantry_items]
    missing = []
    
    for ing in recipe_ingredients:
        if ing.get("required", True):
            ing_name = ing["name"].lower()
            if not any(ing_name in pantry_name for pantry_name in pantry_names):
                missing.append(ing["name"])
    
    return missing

def calculate_recipe_nutrition(ingredients: List[Dict]) -> Dict:
    """Calculate total nutrition for a recipe based on ingredients."""
    total_nutrition = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "fiber": 0,
        "sugar": 0,
        "sodium": 0
    }
    
    for ing in ingredients:
        nutrition_data = get_nutrition_for_ingredient_name(ing["name"])
        if nutrition_data:
            quantity_multiplier = ing["quantity"]  # Simplified - would need unit conversion
            total_nutrition["calories"] += nutrition_data.calories * quantity_multiplier
            total_nutrition["protein"] += nutrition_data.protein_g * quantity_multiplier
            total_nutrition["carbs"] += nutrition_data.carbs_g * quantity_multiplier
            total_nutrition["fat"] += nutrition_data.fat_g * quantity_multiplier
            total_nutrition["fiber"] += nutrition_data.fiber_g * quantity_multiplier
            total_nutrition["sugar"] += nutrition_data.sugar_g * quantity_multiplier
            total_nutrition["sodium"] += nutrition_data.sodium_mg * quantity_multiplier
    
    return total_nutrition

def calculate_recipe_cost(ingredients: List[Dict]) -> float:
    """Calculate estimated cost for a recipe."""
    total_cost = 0.0
    
    for ing in ingredients:
        nutrition_data = get_nutrition_for_ingredient_name(ing["name"])
        if nutrition_data and nutrition_data.cost_per_serving:
            total_cost += nutrition_data.cost_per_serving * ing["quantity"]
        else:
            # Default cost estimate if no data available
            total_cost += 2.0 * ing["quantity"]
    
    return total_cost

def get_nutrition_for_ingredient_name(ingredient_name: str) -> Optional[NutritionData]:
    """Helper to get nutrition data for an ingredient."""
    results = NutritionData.sql(
        "SELECT * FROM nutrition_data WHERE LOWER(ingredient_name) = LOWER(%(name)s) LIMIT 1",
        {"name": ingredient_name}
    )
    
    if results:
        return NutritionData(**results[0])
    return None