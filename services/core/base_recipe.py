from solar import Table, ColumnDetails
from typing import Optional, List, Dict
from datetime import datetime
import uuid

class BaseRecipe(Table):
    __tablename__ = "base_recipes"
    
    id: uuid.UUID = ColumnDetails(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    cuisine_type: str  # e.g., "Mediterranean", "Asian", "American"
    difficulty_level: str  # "easy", "medium", "hard"
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    
    # Core recipe structure
    base_ingredients: List[Dict]  # [{"name": "tomatoes", "quantity": 2, "unit": "cups", "required": true}]
    base_steps: List[Dict]  # [{"step": 1, "instruction": "Preheat oven...", "time_minutes": 5}]
    
    # Branching system
    branch_points: List[Dict]  # [{"step": 3, "question": "Add crunch?", "options": [{"choice": "yes", "modifications": {...}}, {"choice": "no", "modifications": {}}]}]
    
    # Nutrition and cost (base version)
    base_nutrition: Dict  # {"calories": 450, "protein": 25, "carbs": 35, "fat": 20, "fiber": 8}
    base_cost_estimate: float
    
    # Metadata
    dietary_tags: List[str]  # ["vegetarian", "gluten-free", "dairy-free"]
    ingredient_categories: List[str]  # Categories of ingredients used
    image_path: Optional[str] = None  # Hero image for recipe
    created_by: str  # "system" for curated recipes
    created_at: datetime = ColumnDetails(default_factory=datetime.now)
    last_updated: datetime = ColumnDetails(default_factory=datetime.now)