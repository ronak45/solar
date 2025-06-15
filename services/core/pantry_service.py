from typing import List, Dict, Optional
from uuid import UUID
from solar.access import public
from solar.media import MediaFile, save_to_bucket, generate_presigned_url
from openai import OpenAI
import os
import json
from core.pantry_item import PantryItem
from core.nutrition_data import NutritionData

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@public
def scan_pantry_items(image: MediaFile, user_id: str) -> List[Dict]:
    """Scan an image of pantry items and return identified items with suggested details."""
    # Save image to bucket
    image_path = save_to_bucket(image)
    presigned_url = generate_presigned_url(image_path)
    
    # Use OCR to identify items in the image
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash-preview",
        messages=[
            {"role": "system", "content": "You are a food recognition expert. Analyze pantry/kitchen images and identify food items with their approximate quantities."},
            {"role": "user", "content": [
                {
                    "type": "text",
                    "text": "Identify all food items in this pantry image. For each item, estimate the quantity and suggest the appropriate unit of measurement. Focus on packaged goods, fresh produce, and common pantry staples."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": presigned_url}
                }
            ]}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "pantry_scan",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "brand": {"type": ["string", "null"]},
                                    "category": {"type": "string"},
                                    "estimated_quantity": {"type": "number"},
                                    "suggested_unit": {"type": "string"},
                                    "confidence": {"type": "number"}
                                },
                                "required": ["name", "brand", "category", "estimated_quantity", "suggested_unit", "confidence"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["items"],
                    "additionalProperties": False
                }
            }
        }
    )
    
    result = json.loads(response.choices[0].message.content)
    
    # Add image path to each item for reference
    for item in result["items"]:
        item["image_path"] = image_path
        item["user_id"] = user_id
    
    return result["items"]

@public
def add_pantry_item(user_id: str, name: str, category: str, quantity: float, unit: str, 
                   brand: Optional[str] = None, barcode: Optional[str] = None, 
                   image_path: Optional[str] = None, tags: Optional[List[str]] = None) -> PantryItem:
    """Add a new item to the user's pantry inventory."""
    if tags is None:
        tags = []
    
    # Get nutrition data if available
    nutrition_data = get_nutrition_for_ingredient(name)
    nutrition_per_unit = nutrition_data if nutrition_data else None
    
    item = PantryItem(
        user_id=user_id,
        name=name,
        brand=brand,
        category=category,
        quantity=quantity,
        unit=unit,
        barcode=barcode,
        image_path=image_path,
        nutrition_per_unit=nutrition_per_unit,
        tags=tags
    )
    item.sync()
    
    # Return with presigned URL if image exists
    if item.image_path:
        item.image_path = generate_presigned_url(item.image_path)
    
    return item

@public
def get_user_pantry(user_id: str) -> List[PantryItem]:
    """Get all pantry items for a user."""
    results = PantryItem.sql(
        "SELECT * FROM pantry_items WHERE user_id = %(user_id)s ORDER BY category, name",
        {"user_id": user_id}
    )
    
    items = [PantryItem(**result) for result in results]
    
    # Generate presigned URLs for images
    for item in items:
        if item.image_path:
            item.image_path = generate_presigned_url(item.image_path)
    
    return items

@public
def update_pantry_item_quantity(item_id: UUID, new_quantity: float) -> PantryItem:
    """Update the quantity of a pantry item."""
    results = PantryItem.sql(
        "SELECT * FROM pantry_items WHERE id = %(item_id)s",
        {"item_id": str(item_id)}
    )
    
    if not results:
        raise ValueError(f"Pantry item {item_id} not found")
    
    item = PantryItem(**results[0])
    item.quantity = new_quantity
    item.sync()
    
    if item.image_path:
        item.image_path = generate_presigned_url(item.image_path)
    
    return item

@public
def remove_pantry_item(item_id: UUID) -> bool:
    """Remove an item from the pantry."""
    results = PantryItem.sql(
        "DELETE FROM pantry_items WHERE id = %(item_id)s",
        {"item_id": str(item_id)}
    )
    return True

@public
def search_pantry_items(user_id: str, query: str) -> List[PantryItem]:
    """Search pantry items by name, brand, or category."""
    results = PantryItem.sql(
        """SELECT * FROM pantry_items 
           WHERE user_id = %(user_id)s 
           AND (LOWER(name) LIKE LOWER(%(query)s) 
                OR LOWER(brand) LIKE LOWER(%(query)s) 
                OR LOWER(category) LIKE LOWER(%(query)s))
           ORDER BY name""",
        {"user_id": user_id, "query": f"%{query}%"}
    )
    
    items = [PantryItem(**result) for result in results]
    
    for item in items:
        if item.image_path:
            item.image_path = generate_presigned_url(item.image_path)
    
    return items

def get_nutrition_for_ingredient(ingredient_name: str) -> Optional[Dict]:
    """Get nutrition data for an ingredient from the nutrition database."""
    results = NutritionData.sql(
        "SELECT * FROM nutrition_data WHERE LOWER(ingredient_name) = LOWER(%(name)s) LIMIT 1",
        {"name": ingredient_name}
    )
    
    if results:
        nutrition = NutritionData(**results[0])
        return {
            "serving_size": nutrition.serving_size,
            "calories": nutrition.calories,
            "protein_g": nutrition.protein_g,
            "carbs_g": nutrition.carbs_g,
            "fat_g": nutrition.fat_g,
            "fiber_g": nutrition.fiber_g,
            "sugar_g": nutrition.sugar_g,
            "sodium_mg": nutrition.sodium_mg
        }
    
    return None