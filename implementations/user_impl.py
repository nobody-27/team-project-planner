import json
import sys
import os
from pathlib import Path

# Dynamically find the base classes - much better than hardcoding!
def find_base_classes_dir():
    current_dir = Path(__file__).parent.parent
    # Look for user_base.py in parent directories and sibling directories
    for _ in range(3):  # search up to 3 levels up
        for path in current_dir.rglob("user_base.py"):
            return str(path.parent)
        current_dir = current_dir.parent
    return None

base_dir = find_base_classes_dir()
if base_dir:
    sys.path.append(base_dir)

from user_base import UserBase
from storage.json_storage import JsonStorage
from models.user import User
from models.team import TeamMember
from utils.validators import validate_json_string, validate_string_length, validate_required_fields
from utils.exceptions import ValidationError, UniqueConstraintError, NotFoundError

class UserImpl(UserBase):
    """
    Implementation of UserBase - handles all user related operations
    Had to figure out a lot of edge cases while writing this!
    """
    
    def __init__(self):
        self.storage = JsonStorage()
        # might add caching later if performance becomes an issue
        
    def create_user(self, request: str) -> str:
        """Create a new user - took me a while to get the validation right"""
        # Parse and validate input
        try:
            data = validate_json_string(request)
        except Exception as e:
            # probably should log this somewhere
            raise e
            
        validate_required_fields(data, ['name', 'display_name'])
        
        # Validate constraints - these limits are from the requirements
        validate_string_length(data['name'], 'name', 64)
        validate_string_length(data['display_name'], 'display_name', 64)
        
        # Check if username already exists - this was tricky to get right
        existing_users = self.storage.find_by_field('users', 'name', data['name'])
        if len(existing_users) > 0:  # being explicit about the check
            raise UniqueConstraintError(f"User with name '{data['name']}' already exists")
        
        # Create the user object
        user = User(name=data['name'], display_name=data['display_name'])
        self.storage.create('users', user.to_dict())
        
        return json.dumps({"id": user.id})
    
    def list_users(self) -> str:
        """List all users"""
        users = self.storage.read('users')
        result = []
        
        for user_data in users:
            result.append({
                "name": user_data['name'],
                "display_name": user_data['display_name'],
                "creation_time": user_data['creation_time']
            })
        
        return json.dumps(result)
    
    def describe_user(self, request: str) -> str:
        """Get user details by ID"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id'])
        
        user_data = self.storage.find_by_id('users', data['id'])
        if not user_data:
            raise NotFoundError(f"User with id '{data['id']}' not found")
        
        # Note: The docstring mentions 'description' but users don't have descriptions
        # Returning display_name instead as it makes more sense
        result = {
            "name": user_data['name'],
            "description": user_data['display_name'],
            "creation_time": user_data['creation_time']
        }
        
        return json.dumps(result)
    
    def update_user(self, request: str) -> str:
        """Update user display name only"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id', 'user'])
        validate_required_fields(data['user'], ['display_name'])
        
        # Check if user exists
        user_data = self.storage.find_by_id('users', data['id'])
        if not user_data:
            raise NotFoundError(f"User with id '{data['id']}' not found")
        
        # Validate constraints
        if 'name' in data['user'] and data['user']['name'] != user_data['name']:
            raise ValidationError("User name cannot be updated")
        
        validate_string_length(data['user']['display_name'], 'display_name', 128)
        
        # Update user
        updates = {"display_name": data['user']['display_name']}
        self.storage.update('users', data['id'], updates)
        
        return json.dumps({"status": "success"})
    
    def get_user_teams(self, request: str) -> str:
        """Get teams a user belongs to"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id'])
        
        # Check if user exists
        user_data = self.storage.find_by_id('users', data['id'])
        if not user_data:
            raise NotFoundError(f"User with id '{data['id']}' not found")
        
        # Get team memberships
        memberships = self.storage.find_by_field('team_members', 'user_id', data['id'])
        
        # Get team details
        result = []
        teams = self.storage.read('teams')
        
        for membership in memberships:
            for team in teams:
                if team['id'] == membership['team_id']:
                    result.append({
                        "name": team['name'],
                        "description": team['description'],
                        "creation_time": team['creation_time']
                    })
                    break
        
        return json.dumps(result)