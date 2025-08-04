from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
import uuid

@dataclass
class Task:
    """Task model with validation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    user_id: str = ""  # Assigned user
    board_id: str = ""  # Parent board
    status: Literal["OPEN", "IN_PROGRESS", "COMPLETE"] = "OPEN"
    creation_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
            "board_id": self.board_id,
            "status": self.status,
            "creation_time": self.creation_time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Task from dictionary"""
        return cls(**data)