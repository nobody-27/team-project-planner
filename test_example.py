import json
from implementations.user_impl import UserImpl
from implementations.team_impl import TeamImpl
from implementations.project_board_impl import ProjectBoardImpl

def test_basic_workflow():
    """Test basic workflow of the application"""
    print("Testing Team Project Planner...")
    
    # Initialize implementations
    user_mgr = UserImpl()
    team_mgr = TeamImpl()
    board_mgr = ProjectBoardImpl()
    
    try:
        # 1. Create users
        print("\n1. Creating users...")
        user1_response = user_mgr.create_user(json.dumps({
            "name": "john_doe",
            "display_name": "John Doe"
        }))
        user1_id = json.loads(user1_response)['id']
        print(f"Created user: {user1_id}")
        
        user2_response = user_mgr.create_user(json.dumps({
            "name": "jane_smith",
            "display_name": "Jane Smith"
        }))
        user2_id = json.loads(user2_response)['id']
        print(f"Created user: {user2_id}")
        
        # 2. List users
        print("\n2. Listing all users...")
        users = json.loads(user_mgr.list_users())
        for user in users:
            print(f"  - {user['name']} ({user['display_name']})")
        
        # 3. Create team
        print("\n3. Creating team...")
        team_response = team_mgr.create_team(json.dumps({
            "name": "Backend Team",
            "description": "Team responsible for backend development",
            "admin": user1_id
        }))
        team_id = json.loads(team_response)['id']
        print(f"Created team: {team_id}")
        
        # 4. Add users to team
        print("\n4. Adding users to team...")
        team_mgr.add_users_to_team(json.dumps({
            "id": team_id,
            "users": [user2_id]
        }))
        print("Added Jane to the team")
        
        # 5. Create board
        print("\n5. Creating project board...")
        board_response = board_mgr.create_board(json.dumps({
            "name": "Sprint 1",
            "description": "First sprint of the project",
            "team_id": team_id
        }))
        board_id = json.loads(board_response)['id']
        print(f"Created board: {board_id}")
        
        # 6. Add tasks
        print("\n6. Adding tasks...")
        # Note: add_task expects board_id in the request
        task1_response = board_mgr.add_task(json.dumps({
            "title": "Setup Database",
            "description": "Initialize PostgreSQL database",
            "user_id": user1_id,
            "board_id": board_id
        }))
        task1_id = json.loads(task1_response)['id']
        print(f"Created task: {task1_id}")
        
        task2_response = board_mgr.add_task(json.dumps({
            "title": "Create API endpoints",
            "description": "Implement REST API endpoints",
            "user_id": user2_id,
            "board_id": board_id
        }))
        task2_id = json.loads(task2_response)['id']
        print(f"Created task: {task2_id}")
        
        # 7. Update task status
        print("\n7. Updating task status...")
        board_mgr.update_task_status(json.dumps({
            "id": task1_id,
            "status": "IN_PROGRESS"
        }))
        print("Updated task 1 to IN_PROGRESS")
        
        # 8. Export board
        print("\n8. Exporting board...")
        export_response = board_mgr.export_board(json.dumps({
            "id": board_id
        }))
        filename = json.loads(export_response)['out_file']
        print(f"Board exported to: out/{filename}")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {type(e).__name__}: {str(e)}")
        raise

if __name__ == "__main__":
    test_basic_workflow()