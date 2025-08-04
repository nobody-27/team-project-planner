from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal
import uuid


@dataclass
class Board:
    """Board model with validation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    team_id: str = ""
    status: Literal["OPEN", "CLOSED"] = "OPEN"
    creation_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "team_id": self.team_id,
            "status": self.status,
            "creation_time": self.creation_time,
            "end_time": self.end_time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Board from dictionary"""
        return cls(**data)