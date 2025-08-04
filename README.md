# Team Project Planner

A Python-based project management system that provides APIs for managing users, teams, and project boards with tasks.

## Overview

This project implements a complete project management solution extending the provided base classes (`UserBase`, `TeamBase`, `ProjectBoardBase`) with local file storage for persistence.

## Architecture

### Storage Design
- **JSON file storage**: Selected for simplicity and readability
- **Atomic operations**: Implemented write-to-temp-then-rename pattern to prevent data corruption
- **File structure**: Separate files for users, teams, boards, tasks, and team relationships

### Project Structure
```
factwise-python/
├── implementations/          # Core API implementations
│   ├── user_impl.py         
│   ├── team_impl.py         
│   └── project_board_impl.py
├── storage/
│   └── json_storage.py      # File I/O with atomic writes
├── models/                  # Data models
│   ├── user.py
│   ├── team.py
│   ├── board.py
│   └── task.py
├── utils/                   # Utilities
│   ├── validators.py        # Input validation
│   └── exceptions.py        # Custom exceptions
├── db/                      # Data storage directory
└── out/                     # Board export directory
```

## Features

### User Management
- Create users with unique usernames
- List all users with timestamps
- Update user display names
- Track user-team associations

### Team Management
- Create teams with designated admin
- Add/remove team members (max 50 per operation)
- Update team details
- List team members

### Project Board Management
- Create boards for teams
- Add tasks with user assignments
- Update task status (OPEN/IN_PROGRESS/COMPLETE)
- Close boards when all tasks complete
- Export boards with formatted text output

## Implementation Details

### Key Design Decisions

1. **Data Persistence**: JSON files provide sufficient functionality for the requirements while maintaining simplicity
2. **ID Generation**: UUID v4 ensures globally unique identifiers
3. **Timestamp Format**: ISO 8601 for consistency across the system
4. **Validation**: Comprehensive input validation with meaningful error messages
5. **Cross-platform Support**: Compatible with Windows and Unix systems

### API Specifications

All methods accept JSON strings as input and return JSON strings as output, as specified in the base class documentation.

#### Example Usage
```python
from implementations.user_impl import UserImpl
from implementations.team_impl import TeamImpl
from implementations.project_board_impl import ProjectBoardImpl

# Initialize implementations
user_api = UserImpl()
team_api = TeamImpl()
board_api = ProjectBoardImpl()

# Create a user
response = user_api.create_user('{"name": "john_doe", "display_name": "John Doe"}')
# Returns: {"id": "generated-uuid"}
```

## Running the Demo

Execute the demonstration script to see all features in action:
```bash
python demo.py
```

## Technical Considerations

### Performance
- Linear search complexity for data retrieval
- In-memory operations for all data processing
- Suitable for small to medium-sized datasets

### Error Handling
- `ValidationError`: Invalid input format or constraint violations
- `UniqueConstraintError`: Duplicate entity names
- `NotFoundError`: Referenced entity not found
- `ConstraintError`: Business rule violations
- `StorageError`: File system errors

### Assumptions
1. The `add_task` method requires a `board_id` parameter to establish task-board relationships
2. The `describe_user` method returns `display_name` as the description field
3. File locking provides basic concurrency protection suitable for light usage

## Requirements

Python 3.6+ (standard library only, no external dependencies)

## Testing

Run the provided test example:
```bash
python test_example.py
```

---

For additional information, refer to the method documentation in the base classes.