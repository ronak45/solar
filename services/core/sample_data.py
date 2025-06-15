from typing import List
from solar.access import public
from core.base_recipe import BaseRecipe
from core.nutrition_data import NutritionData

@public
def create_sample_recipes() -> List[BaseRecipe]:
    """Create some sample recipes with branching points for demonstration."""
    
    # Sample Recipe 1: Interactive Pasta Dish
    pasta_recipe = BaseRecipe(
        name="Mediterranean Pasta Adventure",
        description="A customizable pasta dish where every choice creates a unique flavor journey",
        cuisine_type="Mediterranean",
        difficulty_level="easy",
        prep_time_minutes=15,
        cook_time_minutes=20,
        servings=4,
        base_ingredients=[
            {"name": "pasta", "quantity": 12, "unit": "oz", "required": True},
            {"name": "olive oil", "quantity": 3, "unit": "tbsp", "required": True},
            {"name": "garlic", "quantity": 3, "unit": "cloves", "required": True},
            {"name": "cherry tomatoes", "quantity": 2, "unit": "cups", "required": True},
            {"name": "fresh basil", "quantity": 0.5, "unit": "cup", "required": False}
        ],
        base_steps=[
            {"step": 1, "instruction": "Bring a large pot of salted water to boil", "time_minutes": 5},
            {"step": 2, "instruction": "Heat olive oil in a large skillet over medium heat", "time_minutes": 2},
            {"step": 3, "instruction": "Add garlic and cook until fragrant", "time_minutes": 1},
            {"step": 4, "instruction": "Add cherry tomatoes and cook until they start to burst", "time_minutes": 5},
            {"step": 5, "instruction": "Cook pasta according to package directions", "time_minutes": 8},
            {"step": 6, "instruction": "Combine pasta with sauce and serve", "time_minutes": 2}
        ],
        branch_points=[
            {
                "step": 3,
                "question": "How would you like to flavor your garlic?",
                "options": [
                    {"choice": "classic", "description": "Keep it simple with just garlic"},
                    {"choice": "spicy", "description": "Add red pepper flakes for heat"},
                    {"choice": "herb", "description": "Add fresh rosemary for earthiness"}
                ]
            },
            {
                "step": 4,
                "question": "What protein would you like to add?",
                "options": [
                    {"choice": "none", "description": "Keep it vegetarian"},
                    {"choice": "chicken", "description": "Add grilled chicken breast"},
                    {"choice": "shrimp", "description": "Add succulent shrimp"}
                ]
            },
            {
                "step": 6,
                "question": "How would you like to finish the dish?",
                "options": [
                    {"choice": "parmesan", "description": "Classic Parmesan cheese"},
                    {"choice": "fresh_herbs", "description": "Fresh basil and parsley"},
                    {"choice": "both", "description": "Cheese and herbs together"}
                ]
            }
        ],
        base_nutrition={
            "calories": 420,
            "protein": 15,
            "carbs": 65,
            "fat": 12,
            "fiber": 4,
            "sugar": 8,
            "sodium": 380
        },
        base_cost_estimate=8.50,
        dietary_tags=["vegetarian"],
        ingredient_categories=["pasta", "vegetables", "herbs"],
        created_by="system"
    )
    
    # Sample Recipe 2: Interactive Stir-Fry
    stirfry_recipe = BaseRecipe(
        name="Asian Fusion Stir-Fry Quest",
        description="Choose your adventure through bold Asian flavors with customizable vegetables and sauces",
        cuisine_type="Asian",
        difficulty_level="medium",
        prep_time_minutes=20,
        cook_time_minutes=15,
        servings=3,
        base_ingredients=[
            {"name": "vegetable oil", "quantity": 2, "unit": "tbsp", "required": True},
            {"name": "ginger", "quantity": 1, "unit": "tbsp", "required": True},
            {"name": "garlic", "quantity": 2, "unit": "cloves", "required": True},
            {"name": "soy sauce", "quantity": 3, "unit": "tbsp", "required": True},
            {"name": "mixed vegetables", "quantity": 4, "unit": "cups", "required": True}
        ],
        base_steps=[
            {"step": 1, "instruction": "Prepare all ingredients (mise en place)", "time_minutes": 15},
            {"step": 2, "instruction": "Heat oil in a wok or large skillet over high heat", "time_minutes": 2},
            {"step": 3, "instruction": "Add aromatics and stir-fry briefly", "time_minutes": 1},
            {"step": 4, "instruction": "Add vegetables in order of cooking time needed", "time_minutes": 5},
            {"step": 5, "instruction": "Add sauce and toss to coat", "time_minutes": 2},
            {"step": 6, "instruction": "Serve immediately over rice", "time_minutes": 1}
        ],
        branch_points=[
            {
                "step": 2,
                "question": "What cooking fat would you prefer?",
                "options": [
                    {"choice": "vegetable_oil", "description": "Neutral vegetable oil for clean flavors"},
                    {"choice": "sesame_oil", "description": "Toasted sesame oil for nutty richness"},
                    {"choice": "peanut_oil", "description": "Peanut oil for high heat and subtle flavor"}
                ]
            },
            {
                "step": 4,
                "question": "Which vegetables combination appeals to you?",
                "options": [
                    {"choice": "classic", "description": "Bell peppers, broccoli, and snap peas"},
                    {"choice": "mushroom", "description": "Mixed mushrooms, bok choy, and carrots"},
                    {"choice": "colorful", "description": "Red cabbage, yellow squash, and snow peas"}
                ]
            },
            {
                "step": 5,
                "question": "How would you like to sauce your stir-fry?",
                "options": [
                    {"choice": "simple_soy", "description": "Classic soy sauce with a touch of sugar"},
                    {"choice": "sweet_sour", "description": "Sweet and sour sauce with pineapple"},
                    {"choice": "spicy_garlic", "description": "Garlic chili sauce for heat lovers"}
                ]
            }
        ],
        base_nutrition={
            "calories": 285,
            "protein": 8,
            "carbs": 35,
            "fat": 14,
            "fiber": 6,
            "sugar": 18,
            "sodium": 920
        },
        base_cost_estimate=12.75,
        dietary_tags=["vegan", "gluten-free"],
        ingredient_categories=["vegetables", "sauces", "aromatics"],
        created_by="system"
    )
    
    # Create the recipes
    recipes = [pasta_recipe, stirfry_recipe]
    BaseRecipe.sync_many(recipes)
    
    return recipes

@public
def create_sample_nutrition_data() -> List[NutritionData]:
    """Create sample nutrition data for common ingredients."""
    
    nutrition_items = [
        NutritionData(
            ingredient_name="pasta",
            serving_size="2 oz dry",
            calories=200,
            protein_g=7,
            carbs_g=42,
            fat_g=1,
            fiber_g=2,
            sugar_g=2,
            sodium_mg=0,
            category="grains",
            data_source="USDA"
        ),
        NutritionData(
            ingredient_name="olive oil",
            serving_size="1 tbsp",
            calories=120,
            protein_g=0,
            carbs_g=0,
            fat_g=14,
            fiber_g=0,
            sugar_g=0,
            sodium_mg=0,
            category="fats",
            data_source="USDA"
        ),
        NutritionData(
            ingredient_name="cherry tomatoes",
            serving_size="1 cup",
            calories=27,
            protein_g=1.3,
            carbs_g=6,
            fat_g=0.3,
            fiber_g=1.8,
            sugar_g=4,
            sodium_mg=7,
            vitamin_c_mg=20,
            category="vegetables",
            data_source="USDA"
        ),
        NutritionData(
            ingredient_name="garlic",
            serving_size="1 clove",
            calories=4,
            protein_g=0.2,
            carbs_g=1,
            fat_g=0,
            fiber_g=0.1,
            sugar_g=0,
            sodium_mg=0,
            category="aromatics",
            data_source="USDA"
        ),
        NutritionData(
            ingredient_name="fresh basil",
            serving_size="2 tbsp chopped",
            calories=1,
            protein_g=0.1,
            carbs_g=0.1,
            fat_g=0,
            fiber_g=0.1,
            sugar_g=0,
            sodium_mg=0,
            vitamin_c_mg=1.8,
            category="herbs",
            data_source="USDA"
        ),
        NutritionData(
            ingredient_name="bell peppers",
            serving_size="1 cup sliced",
            calories=28,
            protein_g=1,
            carbs_g=7,
            fat_g=0.3,
            fiber_g=2.5,
            sugar_g=5,
            sodium_mg=4,
            vitamin_c_mg=120,
            category="vegetables",
            data_source="USDA"
        ),
        NutritionData(
            ingredient_name="broccoli",
            serving_size="1 cup chopped",
            calories=25,
            protein_g=3,
            carbs_g=5,
            fat_g=0.4,
            fiber_g=2.3,
            sugar_g=1.5,
            sodium_mg=33,
            vitamin_c_mg=81,
            category="vegetables",
            data_source="USDA"
        ),
        NutritionData(
            ingredient_name="soy sauce",
            serving_size="1 tbsp",
            calories=8,
            protein_g=1.3,
            carbs_g=0.8,
            fat_g=0,
            fiber_g=0.1,
            sugar_g=0.4,
            sodium_mg=879,
            category="condiments",
            data_source="USDA"
        ),
        NutritionData(
            ingredient_name="chicken breast",
            serving_size="4 oz cooked",
            calories=185,
            protein_g=35,
            carbs_g=0,
            fat_g=4,
            fiber_g=0,
            sugar_g=0,
            sodium_mg=84,
            category="proteins",
            data_source="USDA"
        ),
        NutritionData(
            ingredient_name="shrimp",
            serving_size="4 oz cooked",
            calories=112,
            protein_g=23,
            carbs_g=0,
            fat_g=1.2,
            fiber_g=0,
            sugar_g=0,
            sodium_mg=191,
            category="proteins",
            data_source="USDA"
        )
    ]
    
    NutritionData.sync_many(nutrition_items)
    return nutrition_items