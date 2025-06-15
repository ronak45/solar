from solar import Table, ColumnDetails
from typing import Optional, List, Dict
from datetime import datetime
import uuid

class CookingSession(Table):
    __tablename__ = "cooking_sessions"
    
    id: uuid.UUID = ColumnDetails(default_factory=uuid.uuid4, primary_key=True)
    user_id: str  # Reference to Solar auth user
    base_recipe_id: uuid.UUID  # Reference to base recipe
    
    # Session tracking
    status: str  # "in_progress", "completed", "abandoned"
    started_at: datetime = ColumnDetails(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # User choices and path taken
    decisions_made: List[Dict]  # [{"branch_point": 1, "choice": "yes", "timestamp": "2025-01-01T12:00:00"}]
    current_step: int  # Current step in the recipe
    
    # Final recipe state after all decisions
    final_ingredients: List[Dict]  # Final ingredient list after all branches
    final_steps: List[Dict]  # Final cooking steps after all branches
    final_nutrition: Dict  # Final nutrition facts
    final_cost: float  # Final cost estimate
    total_time_minutes: int  # Actual time taken
    
    # Session documentation
    session_photos: List[str]  # Paths to photos taken during cooking
    voice_interactions: List[Dict]  # [{"timestamp": "...", "question": "...", "response": "..."}]
    notes: Optional[str] = None  # User notes about the session
    
    # Sharing and replay
    shared: bool = False
    share_url: Optional[str] = None
    rating: Optional[int] = None  # 1-5 stars
    would_make_again: Optional[bool] = None
    
    created_at: datetime = ColumnDetails(default_factory=datetime.now)
    last_updated: datetime = ColumnDetails(default_factory=datetime.now)