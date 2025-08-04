from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class User:
    """User model with validation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    display_name: str = ""
    creation_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "creation_time": self.creation_time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create User from dictionary"""
        return cls(**data)