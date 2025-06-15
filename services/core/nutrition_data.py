from solar import Table, ColumnDetails
from typing import Optional, Dict
from datetime import datetime
import uuid

class NutritionData(Table):
    __tablename__ = "nutrition_data"
    
    id: uuid.UUID = ColumnDetails(default_factory=uuid.uuid4, primary_key=True)
    ingredient_name: str  # Canonical ingredient name
    serving_size: str  # e.g., "1 cup", "100g", "1 medium"
    
    # Macronutrients (per serving)
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sugar_g: float
    sodium_mg: float
    
    # Micronutrients (per serving) - optional but valuable
    vitamin_c_mg: Optional[float] = None
    vitamin_a_iu: Optional[float] = None
    calcium_mg: Optional[float] = None
    iron_mg: Optional[float] = None
    potassium_mg: Optional[float] = None
    
    # Additional data
    cost_per_serving: Optional[float] = None
    allergens: Optional[str] = None  # Common allergens as comma-separated string
    category: str  # "vegetable", "fruit", "protein", "grain", "dairy", "spice"
    
    # Data source and reliability
    data_source: str  # "USDA", "manual_entry", "estimated"
    verified: bool = False
    
    created_at: datetime = ColumnDetails(default_factory=datetime.now)
    last_updated: datetime = ColumnDetails(default_factory=datetime.now)