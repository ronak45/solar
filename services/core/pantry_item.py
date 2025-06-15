from solar import Table, ColumnDetails
from typing import Optional, List, Dict
from datetime import datetime, date
import uuid

class PantryItem(Table):
    __tablename__ = "pantry_items"
    
    id: uuid.UUID = ColumnDetails(default_factory=uuid.uuid4, primary_key=True)
    user_id: str  # Reference to Solar auth user
    name: str
    brand: Optional[str] = None
    category: str  # e.g., "vegetables", "spices", "proteins", "grains"
    quantity: float
    unit: str  # e.g., "cups", "lbs", "pieces", "ml"
    expiration_date: Optional[date] = None
    barcode: Optional[str] = None
    image_path: Optional[str] = None  # Path to image in media bucket
    nutrition_per_unit: Optional[Dict] = None  # Nutrition facts per unit
    cost_per_unit: Optional[float] = None
    tags: List[str]  # e.g., ["organic", "gluten-free", "vegan"]
    last_updated: datetime = ColumnDetails(default_factory=datetime.now)
    created_at: datetime = ColumnDetails(default_factory=datetime.now)