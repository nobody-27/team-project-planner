from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid

@dataclass
class Team:
    """Team model with validation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    admin: str = ""  # User ID
    creation_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "admin": self.admin,
            "creation_time": self.creation_time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Team from dictionary"""
        return cls(**data)

@dataclass
class TeamMember:
    """Team-User relationship"""
    team_id: str
    user_id: str
    
    def to_dict(self):
        return {
            "team_id": self.team_id,
            "user_id": self.user_id
        }