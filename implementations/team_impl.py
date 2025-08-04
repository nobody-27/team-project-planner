import json
import sys
import os
from pathlib import Path

# Dynamically find the base classes directory
def find_base_classes_dir():
    current_dir = Path(__file__).parent.parent
    for _ in range(3):  # search up to 3 levels up
        for path in current_dir.rglob("team_base.py"):
            return str(path.parent)
        current_dir = current_dir.parent
    return None

base_dir = find_base_classes_dir()
if base_dir:
    sys.path.append(base_dir)

from team_base import TeamBase
from storage.json_storage import JsonStorage
from models.team import Team, TeamMember
from utils.validators import validate_json_string, validate_string_length, validate_required_fields, validate_id_format
from utils.exceptions import ValidationError, UniqueConstraintError, NotFoundError, ConstraintError

class TeamImpl(TeamBase):
    """Concrete implementation of TeamBase"""
    
    def __init__(self):
        self.storage = JsonStorage()
        
    def create_team(self, request: str) -> str:
        """Create a new team"""
        # Parse and validate input
        data = validate_json_string(request)
        validate_required_fields(data, ['name', 'description', 'admin'])
        
        # Validate constraints
        validate_string_length(data['name'], 'name', 64)
        validate_string_length(data['description'], 'description', 128)
        
        # Check if admin user exists
        admin_user = self.storage.find_by_id('users', data['admin'])
        if not admin_user:
            raise NotFoundError(f"Admin user with id '{data['admin']}' not found")
        
        # Check unique constraint
        existing_teams = self.storage.find_by_field('teams', 'name', data['name'])
        if existing_teams:
            raise UniqueConstraintError(f"Team with name '{data['name']}' already exists")
        
        # Create team
        team = Team(
            name=data['name'],
            description=data['description'],
            admin=data['admin']
        )
        self.storage.create('teams', team.to_dict())
        
        # Add admin as team member
        member = TeamMember(team_id=team.id, user_id=data['admin'])
        self.storage.create('team_members', member.to_dict())
        
        return json.dumps({"id": team.id})
    
    def list_teams(self) -> str:
        """List all teams"""
        teams = self.storage.read('teams')
        result = []
        
        for team_data in teams:
            result.append({
                "name": team_data['name'],
                "description": team_data['description'],
                "creation_time": team_data['creation_time'],
                "admin": team_data['admin']
            })
        
        return json.dumps(result)
    
    def describe_team(self, request: str) -> str:
        """Get team details by ID"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id'])
        
        team_data = self.storage.find_by_id('teams', data['id'])
        if not team_data:
            raise NotFoundError(f"Team with id '{data['id']}' not found")
        
        result = {
            "name": team_data['name'],
            "description": team_data['description'],
            "creation_time": team_data['creation_time'],
            "admin": team_data['admin']
        }
        
        return json.dumps(result)
    
    def update_team(self, request: str) -> str:
        """Update team details"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id', 'team'])
        
        # Check if team exists
        team_data = self.storage.find_by_id('teams', data['id'])
        if not team_data:
            raise NotFoundError(f"Team with id '{data['id']}' not found")
        
        updates = {}
        
        # Handle name update
        if 'name' in data['team']:
            validate_string_length(data['team']['name'], 'name', 64)
            # Check unique constraint
            if data['team']['name'] != team_data['name']:
                existing_teams = self.storage.find_by_field('teams', 'name', data['team']['name'])
                if existing_teams:
                    raise UniqueConstraintError(f"Team with name '{data['team']['name']}' already exists")
            updates['name'] = data['team']['name']
        
        # Handle description update
        if 'description' in data['team']:
            validate_string_length(data['team']['description'], 'description', 128)
            updates['description'] = data['team']['description']
        
        # Handle admin update
        if 'admin' in data['team']:
            # Check if new admin exists
            admin_user = self.storage.find_by_id('users', data['team']['admin'])
            if not admin_user:
                raise NotFoundError(f"Admin user with id '{data['team']['admin']}' not found")
            updates['admin'] = data['team']['admin']
        
        # Update team
        if updates:
            self.storage.update('teams', data['id'], updates)
        
        return json.dumps({"status": "success"})
    
    def add_users_to_team(self, request: str):
        """Add users to team"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id', 'users'])
        
        # Check if team exists
        team_data = self.storage.find_by_id('teams', data['id'])
        if not team_data:
            raise NotFoundError(f"Team with id '{data['id']}' not found")
        
        # Validate user limit
        if len(data['users']) > 50:
            raise ConstraintError("Cannot add more than 50 users at once")
        
        # Get current team members
        current_members = self.storage.find_by_field('team_members', 'team_id', data['id'])
        current_member_ids = {m['user_id'] for m in current_members}
        
        # Add new members
        added = 0
        for user_id in data['users']:
            # Check if user exists
            user = self.storage.find_by_id('users', user_id)
            if not user:
                continue  # Skip non-existent users
            
            # Check if already a member
            if user_id not in current_member_ids:
                member = TeamMember(team_id=data['id'], user_id=user_id)
                self.storage.create('team_members', member.to_dict())
                added += 1
        
        return json.dumps({"added": added})
    
    def remove_users_from_team(self, request: str):
        """Remove users from team"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id', 'users'])
        
        # Check if team exists
        team_data = self.storage.find_by_id('teams', data['id'])
        if not team_data:
            raise NotFoundError(f"Team with id '{data['id']}' not found")
        
        # Validate user limit
        if len(data['users']) > 50:
            raise ConstraintError("Cannot remove more than 50 users at once")
        
        # Get all team members
        all_members = self.storage.read('team_members')
        removed = 0
        
        # Filter out users to be removed
        updated_members = []
        for member in all_members:
            if member['team_id'] == data['id'] and member['user_id'] in data['users']:
                removed += 1
            else:
                updated_members.append(member)
        
        # Write back updated members
        self.storage.write('team_members', updated_members)
        
        return json.dumps({"removed": removed})
    
    def list_team_users(self, request: str):
        """List users in a team"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id'])
        
        # Check if team exists
        team_data = self.storage.find_by_id('teams', data['id'])
        if not team_data:
            raise NotFoundError(f"Team with id '{data['id']}' not found")
        
        # Get team members
        members = self.storage.find_by_field('team_members', 'team_id', data['id'])
        
        # Get user details
        result = []
        users = self.storage.read('users')
        
        for member in members:
            for user in users:
                if user['id'] == member['user_id']:
                    result.append({
                        "id": user['id'],
                        "name": user['name'],
                        "display_name": user['display_name']
                    })
                    break
        
        return json.dumps(result)