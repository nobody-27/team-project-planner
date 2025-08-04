import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Dynamically find the base classes directory
def find_base_classes_dir():
    current_dir = Path(__file__).parent.parent
    for _ in range(3):  # search up to 3 levels up
        for path in current_dir.rglob("project_board_base.py"):
            return str(path.parent)
        current_dir = current_dir.parent
    return None

base_dir = find_base_classes_dir()
if base_dir:
    sys.path.append(base_dir)

from project_board_base import ProjectBoardBase
from storage.json_storage import JsonStorage
from models.board import Board
from models.task import Task
from utils.validators import validate_json_string, validate_string_length, validate_required_fields
from utils.exceptions import ValidationError, UniqueConstraintError, NotFoundError, ConstraintError

class ProjectBoardImpl(ProjectBoardBase):
    """
    Project board implementation - this one was fun to build!
    The export_board method took me forever to get right with the ASCII art
    """
    
    def __init__(self):
        self.storage = JsonStorage()
        # Make sure we have a place to put exported files
        self.out_dir = Path("out")
        self.out_dir.mkdir(exist_ok=True)
        
    def create_board(self, request: str):
        """Create a new board"""
        # Parse and validate input
        data = validate_json_string(request)
        validate_required_fields(data, ['name', 'description', 'team_id'])
        
        # Validate constraints
        validate_string_length(data['name'], 'name', 64)
        validate_string_length(data['description'], 'description', 128)
        
        # Check if team exists
        team = self.storage.find_by_id('teams', data['team_id'])
        if not team:
            raise NotFoundError(f"Team with id '{data['team_id']}' not found")
        
        # Check unique constraint (board name must be unique within team)
        team_boards = self.storage.find_by_field('boards', 'team_id', data['team_id'])
        for board in team_boards:
            if board['name'] == data['name'] and board['status'] == 'OPEN':
                raise UniqueConstraintError(f"Board with name '{data['name']}' already exists in this team")
        
        # Create board
        board = Board(
            name=data['name'],
            description=data['description'],
            team_id=data['team_id']
        )
        
        # Override creation_time if provided
        if 'creation_time' in data:
            board.creation_time = data['creation_time']
        
        self.storage.create('boards', board.to_dict())
        
        return json.dumps({"id": board.id})
    
    def close_board(self, request: str) -> str:
        """Close a board"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id'])
        
        # Check if board exists
        board_data = self.storage.find_by_id('boards', data['id'])
        if not board_data:
            raise NotFoundError(f"Board with id '{data['id']}' not found")
        
        # Check if already closed
        if board_data['status'] == 'CLOSED':
            raise ConstraintError("Board is already closed")
        
        # Check if all tasks are complete
        tasks = self.storage.find_by_field('tasks', 'board_id', data['id'])
        incomplete_tasks = [t for t in tasks if t['status'] != 'COMPLETE']
        
        if incomplete_tasks:
            raise ConstraintError("Cannot close board with incomplete tasks")
        
        # Close the board
        updates = {
            'status': 'CLOSED',
            'end_time': datetime.utcnow().isoformat()
        }
        self.storage.update('boards', data['id'], updates)
        
        return json.dumps({"status": "success"})
    
    def add_task(self, request: str) -> str:
        """Add a task to a board"""
        data = validate_json_string(request)
        validate_required_fields(data, ['title', 'description', 'user_id'])
        
        # Validate constraints
        validate_string_length(data['title'], 'title', 64)
        validate_string_length(data['description'], 'description', 128)
        
        # Determine board_id from context or request
        # Since the docstring mentions board context but doesn't include board_id in params,
        # we'll need to infer this. For now, assuming it's passed somehow.
        # In a real implementation, this might come from session context.
        board_id = data.get('board_id')
        if not board_id:
            raise ValidationError("board_id is required")
        
        # Check if board exists and is open
        board = self.storage.find_by_id('boards', board_id)
        if not board:
            raise NotFoundError(f"Board with id '{board_id}' not found")
        
        if board['status'] != 'OPEN':
            raise ConstraintError("Can only add tasks to OPEN boards")
        
        # Check if user exists
        user = self.storage.find_by_id('users', data['user_id'])
        if not user:
            raise NotFoundError(f"User with id '{data['user_id']}' not found")
        
        # Check unique constraint (task title must be unique within board)
        board_tasks = self.storage.find_by_field('tasks', 'board_id', board_id)
        for task in board_tasks:
            if task['title'] == data['title']:
                raise UniqueConstraintError(f"Task with title '{data['title']}' already exists in this board")
        
        # Create task
        task = Task(
            title=data['title'],
            description=data['description'],
            user_id=data['user_id'],
            board_id=board_id
        )
        
        # Override creation_time if provided
        if 'creation_time' in data:
            task.creation_time = data['creation_time']
        
        self.storage.create('tasks', task.to_dict())
        
        return json.dumps({"id": task.id})
    
    def update_task_status(self, request: str):
        """Update task status"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id', 'status'])
        
        # Validate status
        valid_statuses = ['OPEN', 'IN_PROGRESS', 'COMPLETE']
        if data['status'] not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        # Check if task exists
        task = self.storage.find_by_id('tasks', data['id'])
        if not task:
            raise NotFoundError(f"Task with id '{data['id']}' not found")
        
        # Update task status
        self.storage.update('tasks', data['id'], {'status': data['status']})
        
        return json.dumps({"status": "success"})
    
    def list_boards(self, request: str) -> str:
        """List all open boards for a team"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id'])  # team_id
        
        # Check if team exists
        team = self.storage.find_by_id('teams', data['id'])
        if not team:
            raise NotFoundError(f"Team with id '{data['id']}' not found")
        
        # Get open boards for the team
        all_boards = self.storage.find_by_field('boards', 'team_id', data['id'])
        open_boards = [b for b in all_boards if b['status'] == 'OPEN']
        
        result = []
        for board in open_boards:
            result.append({
                "id": board['id'],
                "name": board['name']
            })
        
        return json.dumps(result)
    
    def export_board(self, request: str) -> str:
        """Export board to a text file with creative formatting - this was the fun part!"""
        data = validate_json_string(request)
        validate_required_fields(data, ['id'])
        
        # Get the board first
        board = self.storage.find_by_id('boards', data['id'])
        if not board:
            raise NotFoundError(f"Board with id '{data['id']}' not found")
        
        # Get team info
        team = self.storage.find_by_id('teams', board['team_id'])
        team_name = team['name'] if team else "Unknown Team"  # fallback just in case
        
        # Get all tasks for this board
        tasks = self.storage.find_by_field('tasks', 'board_id', data['id'])
        
        # Sort tasks by status - makes the output look nicer
        open_tasks = []
        in_progress_tasks = []
        complete_tasks = []
        
        # Build user lookup map for performance
        users = self.storage.read('users')
        user_map = {u['id']: u['display_name'] for u in users}
        
        # Group tasks by their status
        for task in tasks:
            task_info = {
                'title': task['title'],
                'user': user_map.get(task['user_id'], 'Unassigned')  # handle missing users
            }
            
            # Could probably use a dictionary here but this is clearer
            if task['status'] == 'OPEN':
                open_tasks.append(task_info)
            elif task['status'] == 'IN_PROGRESS':
                in_progress_tasks.append(task_info)
            else:  # COMPLETE
                complete_tasks.append(task_info)
        
        # Create formatted output
        output = []
        output.append("╔" + "═" * 60 + "╗")
        output.append(f"║{' BOARD: ' + board['name']:^60}║")
        output.append(f"║{' Team: ' + team_name:^60}║")
        output.append(f"║{' Status: ' + board['status']:^60}║")
        output.append("╠" + "═" * 60 + "╣")
        output.append(f"║{' Description:':60}║")
        
        # Wrap description
        desc_words = board['description'].split()
        desc_line = ""
        for word in desc_words:
            if len(desc_line) + len(word) + 1 <= 58:
                desc_line += word + " "
            else:
                output.append(f"║ {desc_line:<58} ║")
                desc_line = word + " "
        if desc_line:
            output.append(f"║ {desc_line:<58} ║")
        
        output.append("╠" + "═" * 60 + "╣")
        
        # Add tasks by status
        if open_tasks:
            output.append(f"║ {'OPEN (' + str(len(open_tasks)) + ')':58} ║")
            for task in open_tasks:
                output.append(f"║  • {task['title'][:40]:<40} ({task['user'][:14]:<14}) ║")
            output.append("║" + " " * 60 + "║")
        
        if in_progress_tasks:
            output.append(f"║ {'IN PROGRESS (' + str(len(in_progress_tasks)) + ')':58} ║")
            for task in in_progress_tasks:
                output.append(f"║  ◐ {task['title'][:40]:<40} ({task['user'][:14]:<14}) ║")
            output.append("║" + " " * 60 + "║")
        
        if complete_tasks:
            output.append(f"║ {'COMPLETE (' + str(len(complete_tasks)) + ')':58} ║")
            for task in complete_tasks:
                output.append(f"║  ✓ {task['title'][:40]:<40} ({task['user'][:14]:<14}) ║")
        
        output.append("╠" + "═" * 60 + "╣")
        output.append(f"║ Created: {board['creation_time'][:19]:58} ║")
        if board.get('end_time'):
            output.append(f"║ Closed: {board['end_time'][:19]:58} ║")
        output.append("╚" + "═" * 60 + "╝")
        
        # Write to file
        filename = f"board_{board['id'][:8]}_{board['name'].replace(' ', '_')}.txt"
        file_path = self.out_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))
        
        return json.dumps({"out_file": filename})