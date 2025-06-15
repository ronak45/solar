from typing import List, Dict, Optional
from uuid import UUID
from solar.access import public
from openai import OpenAI
import os
import json
from core.nutrition_data import NutritionData

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@public
def add_nutrition_data(ingredient_name: str, serving_size: str, calories: float, 
                      protein_g: float, carbs_g: float, fat_g: float, fiber_g: float,
                      sugar_g: float, sodium_mg: float, category: str,
                      vitamin_c_mg: Optional[float] = None, vitamin_a_iu: Optional[float] = None,
                      calcium_mg: Optional[float] = None, iron_mg: Optional[float] = None,
                      potassium_mg: Optional[float] = None, cost_per_serving: Optional[float] = None,
                      allergens: Optional[str] = None, data_source: str = "manual_entry") -> NutritionData:
    """Add nutrition data for an ingredient."""
    nutrition = NutritionData(
        ingredient_name=ingredient_name,
        serving_size=serving_size,
        calories=calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        fiber_g=fiber_g,
        sugar_g=sugar_g,
        sodium_mg=sodium_mg,
        vitamin_c_mg=vitamin_c_mg,
        vitamin_a_iu=vitamin_a_iu,
        calcium_mg=calcium_mg,
        iron_mg=iron_mg,
        potassium_mg=potassium_mg,
        cost_per_serving=cost_per_serving,
        allergens=allergens,
        category=category,
        data_source=data_source
    )
    nutrition.sync()
    return nutrition

@public
def get_nutrition_data(ingredient_name: str) -> Optional[NutritionData]:
    """Get nutrition data for a specific ingredient."""
    results = NutritionData.sql(
        "SELECT * FROM nutrition_data WHERE LOWER(ingredient_name) = LOWER(%(name)s) LIMIT 1",
        {"name": ingredient_name}
    )
    
    if results:
        return NutritionData(**results[0])
    return None

@public
def search_nutrition_data(query: str) -> List[NutritionData]:
    """Search nutrition data by ingredient name or category."""
    results = NutritionData.sql(
        """SELECT * FROM nutrition_data 
           WHERE LOWER(ingredient_name) LIKE LOWER(%(query)s) 
           OR LOWER(category) LIKE LOWER(%(query)s)
           ORDER BY ingredient_name LIMIT 20""",
        {"query": f"%{query}%"}
    )
    
    return [NutritionData(**result) for result in results]

@public
def calculate_recipe_nutrition(ingredients: List[Dict]) -> Dict:
    """Calculate total nutrition for a recipe given its ingredients."""
    total_nutrition = {
        "calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fat_g": 0,
        "fiber_g": 0,
        "sugar_g": 0,
        "sodium_mg": 0,
        "vitamin_c_mg": 0,
        "vitamin_a_iu": 0,
        "calcium_mg": 0,
        "iron_mg": 0,
        "potassium_mg": 0
    }
    
    for ingredient in ingredients:
        nutrition_data = get_nutrition_data(ingredient["name"])
        if nutrition_data:
            # Get quantity multiplier (simplified - would need proper unit conversion)
            multiplier = ingredient.get("quantity", 1)
            
            total_nutrition["calories"] += nutrition_data.calories * multiplier
            total_nutrition["protein_g"] += nutrition_data.protein_g * multiplier
            total_nutrition["carbs_g"] += nutrition_data.carbs_g * multiplier
            total_nutrition["fat_g"] += nutrition_data.fat_g * multiplier
            total_nutrition["fiber_g"] += nutrition_data.fiber_g * multiplier
            total_nutrition["sugar_g"] += nutrition_data.sugar_g * multiplier
            total_nutrition["sodium_mg"] += nutrition_data.sodium_mg * multiplier
            
            # Add micronutrients if available
            if nutrition_data.vitamin_c_mg:
                total_nutrition["vitamin_c_mg"] += nutrition_data.vitamin_c_mg * multiplier
            if nutrition_data.vitamin_a_iu:
                total_nutrition["vitamin_a_iu"] += nutrition_data.vitamin_a_iu * multiplier
            if nutrition_data.calcium_mg:
                total_nutrition["calcium_mg"] += nutrition_data.calcium_mg * multiplier
            if nutrition_data.iron_mg:
                total_nutrition["iron_mg"] += nutrition_data.iron_mg * multiplier
            if nutrition_data.potassium_mg:
                total_nutrition["potassium_mg"] += nutrition_data.potassium_mg * multiplier
    
    return total_nutrition

@public
def estimate_nutrition_from_llm(ingredient_name: str, serving_size: str) -> Dict:
    """Use LLM to estimate nutrition data for ingredients not in the database."""
    response = client.chat.completions.create(
        model="openai/o4-mini",
        messages=[
            {"role": "system", "content": "You are a nutrition expert. Provide accurate nutrition estimates for food ingredients."},
            {"role": "user", "content": f"Provide nutrition information for {ingredient_name}, serving size: {serving_size}. Base your estimates on USDA nutrition data."}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "nutrition_estimate",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "calories": {"type": "number"},
                        "protein_g": {"type": "number"},
                        "carbs_g": {"type": "number"},
                        "fat_g": {"type": "number"},
                        "fiber_g": {"type": "number"},
                        "sugar_g": {"type": "number"},
                        "sodium_mg": {"type": "number"},
                        "category": {"type": "string"},
                        "confidence": {"type": "string"}
                    },
                    "required": ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g", "sodium_mg", "category", "confidence"],
                    "additionalProperties": False
                }
            }
        }
    )
    
    return json.loads(response.choices[0].message.content)

@public
def bulk_import_nutrition_data(nutrition_list: List[Dict]) -> List[NutritionData]:
    """Bulk import nutrition data from a list."""
    nutrition_objects = []
    
    for data in nutrition_list:
        nutrition = NutritionData(
            ingredient_name=data["ingredient_name"],
            serving_size=data["serving_size"],
            calories=data["calories"],
            protein_g=data["protein_g"],
            carbs_g=data["carbs_g"],
            fat_g=data["fat_g"],
            fiber_g=data["fiber_g"],
            sugar_g=data["sugar_g"],
            sodium_mg=data["sodium_mg"],
            vitamin_c_mg=data.get("vitamin_c_mg"),
            vitamin_a_iu=data.get("vitamin_a_iu"),
            calcium_mg=data.get("calcium_mg"),
            iron_mg=data.get("iron_mg"),
            potassium_mg=data.get("potassium_mg"),
            cost_per_serving=data.get("cost_per_serving"),
            allergens=data.get("allergens"),
            category=data["category"],
            data_source=data.get("data_source", "bulk_import")
        )
        nutrition_objects.append(nutrition)
    
    # Use batch insert for efficiency
    NutritionData.sync_many(nutrition_objects)
    return nutrition_objects

@public
def get_nutrition_by_category(category: str) -> List[NutritionData]:
    """Get all nutrition data for a specific category."""
    results = NutritionData.sql(
        "SELECT * FROM nutrition_data WHERE LOWER(category) = LOWER(%(category)s) ORDER BY ingredient_name",
        {"category": category}
    )
    
    return [NutritionData(**result) for result in results]

@public
def update_nutrition_cost(ingredient_name: str, cost_per_serving: float) -> Optional[NutritionData]:
    """Update the cost per serving for an ingredient."""
    results = NutritionData.sql(
        "SELECT * FROM nutrition_data WHERE LOWER(ingredient_name) = LOWER(%(name)s) LIMIT 1",
        {"name": ingredient_name}
    )
    
    if results:
        nutrition = NutritionData(**results[0])
        nutrition.cost_per_serving = cost_per_serving
        nutrition.sync()
        return nutrition
    
    return None

@public
def analyze_dietary_compatibility(ingredients: List[str], dietary_restrictions: List[str]) -> Dict:
    """Analyze if a recipe is compatible with dietary restrictions."""
    compatibility = {
        "compatible": True,
        "issues": [],
        "suggestions": []
    }
    
    for ingredient in ingredients:
        nutrition_data = get_nutrition_data(ingredient)
        if nutrition_data and nutrition_data.allergens:
            allergens = nutrition_data.allergens.lower().split(", ")
            
            for restriction in dietary_restrictions:
                restriction_lower = restriction.lower()
                
                # Check common dietary restrictions
                if restriction_lower == "gluten-free" and "gluten" in allergens:
                    compatibility["compatible"] = False
                    compatibility["issues"].append(f"{ingredient} contains gluten")
                elif restriction_lower == "dairy-free" and any(dairy in allergens for dairy in ["milk", "dairy", "lactose"]):
                    compatibility["compatible"] = False
                    compatibility["issues"].append(f"{ingredient} contains dairy")
                elif restriction_lower == "nut-free" and any(nut in allergens for nut in ["nuts", "peanuts", "tree nuts"]):
                    compatibility["compatible"] = False
                    compatibility["issues"].append(f"{ingredient} contains nuts")
    
    return compatibility