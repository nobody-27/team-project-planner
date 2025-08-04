"""
Demonstration of the Team Project Planner APIs
This shows how to use all the implemented methods
"""

import json
from implementations.user_impl import UserImpl
from implementations.team_impl import TeamImpl
from implementations.project_board_impl import ProjectBoardImpl

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def demo():
    # Initialize the API implementations
    user_api = UserImpl()
    team_api = TeamImpl()
    board_api = ProjectBoardImpl()
    
    print("TEAM PROJECT PLANNER - API DEMONSTRATION")
    
    # ========== USER MANAGEMENT APIs ==========
    print_section("USER MANAGEMENT APIs")
    
    # 1. Create Users
    print("\n1. Creating users using create_user() API:")
    
    # Create first user
    user1_request = json.dumps({
        "name": "alice_cooper",
        "display_name": "Alice Cooper"
    })
    user1_response = user_api.create_user(user1_request)
    alice_id = json.loads(user1_response)['id']
    print(f"   Request: {user1_request}")
    print(f"   Response: {user1_response}")
    
    # Create second user
    user2_request = json.dumps({
        "name": "bob_builder",
        "display_name": "Bob the Builder"
    })
    user2_response = user_api.create_user(user2_request)
    bob_id = json.loads(user2_response)['id']
    print(f"   Request: {user2_request}")
    print(f"   Response: {user2_response}")
    
    # Create third user
    user3_request = json.dumps({
        "name": "charlie_brown",
        "display_name": "Charlie Brown"
    })
    user3_response = user_api.create_user(user3_request)
    charlie_id = json.loads(user3_response)['id']
    print(f"   Request: {user3_request}")
    print(f"   Response: {user3_response}")
    
    # 2. List Users
    print("\n2. Listing all users using list_users() API:")
    users_list = user_api.list_users()
    print(f"   Response: {users_list}")
    
    # 3. Describe User
    print("\n3. Getting user details using describe_user() API:")
    describe_request = json.dumps({"id": alice_id})
    describe_response = user_api.describe_user(describe_request)
    print(f"   Request: {describe_request}")
    print(f"   Response: {describe_response}")
    
    # 4. Update User
    print("\n4. Updating user using update_user() API:")
    update_request = json.dumps({
        "id": bob_id,
        "user": {
            "display_name": "Bob the Master Builder"
        }
    })
    update_response = user_api.update_user(update_request)
    print(f"   Request: {update_request}")
    print(f"   Response: {update_response}")
    
    # Verify update
    print("   Verifying update:")
    users_list_after = user_api.list_users()
    print(f"   Updated list: {users_list_after}")
    
    # ========== TEAM MANAGEMENT APIs ==========
    print_section("TEAM MANAGEMENT APIs")
    
    # 1. Create Team
    print("\n1. Creating team using create_team() API:")
    team_request = json.dumps({
        "name": "Development Team",
        "description": "Main development team for the project",
        "admin": alice_id
    })
    team_response = team_api.create_team(team_request)
    dev_team_id = json.loads(team_response)['id']
    print(f"   Request: {team_request}")
    print(f"   Response: {team_response}")
    
    # Create another team
    team2_request = json.dumps({
        "name": "QA Team",
        "description": "Quality assurance and testing team",
        "admin": charlie_id
    })
    team2_response = team_api.create_team(team2_request)
    qa_team_id = json.loads(team2_response)['id']
    print(f"   Request: {team2_request}")
    print(f"   Response: {team2_response}")
    
    # 2. List Teams
    print("\n2. Listing all teams using list_teams() API:")
    teams_list = team_api.list_teams()
    print(f"   Response: {teams_list}")
    
    # 3. Describe Team
    print("\n3. Getting team details using describe_team() API:")
    team_describe_request = json.dumps({"id": dev_team_id})
    team_describe_response = team_api.describe_team(team_describe_request)
    print(f"   Request: {team_describe_request}")
    print(f"   Response: {team_describe_response}")
    
    # 4. Add Users to Team
    print("\n4. Adding users to team using add_users_to_team() API:")
    add_users_request = json.dumps({
        "id": dev_team_id,
        "users": [bob_id, charlie_id]
    })
    add_users_response = team_api.add_users_to_team(add_users_request)
    print(f"   Request: {add_users_request}")
    print(f"   Response: {add_users_response}")
    
    # 5. List Team Users
    print("\n5. Listing team members using list_team_users() API:")
    list_members_request = json.dumps({"id": dev_team_id})
    list_members_response = team_api.list_team_users(list_members_request)
    print(f"   Request: {list_members_request}")
    print(f"   Response: {list_members_response}")
    
    # 6. Get User Teams
    print("\n6. Getting user's teams using get_user_teams() API:")
    user_teams_request = json.dumps({"id": alice_id})
    user_teams_response = user_api.get_user_teams(user_teams_request)
    print(f"   Request: {user_teams_request}")
    print(f"   Response: {user_teams_response}")
    
    # 7. Update Team
    print("\n7. Updating team using update_team() API:")
    team_update_request = json.dumps({
        "id": dev_team_id,
        "team": {
            "description": "Elite development team for cutting-edge projects",
            "admin": bob_id
        }
    })
    team_update_response = team_api.update_team(team_update_request)
    print(f"   Request: {team_update_request}")
    print(f"   Response: {team_update_response}")
    
    # 8. Remove Users from Team
    print("\n8. Removing users from team using remove_users_from_team() API:")
    remove_users_request = json.dumps({
        "id": dev_team_id,
        "users": [charlie_id]
    })
    remove_users_response = team_api.remove_users_from_team(remove_users_request)
    print(f"   Request: {remove_users_request}")
    print(f"   Response: {remove_users_response}")
    
    # ========== PROJECT BOARD APIs ==========
    print_section("PROJECT BOARD APIs")
    
    # 1. Create Board
    print("\n1. Creating board using create_board() API:")
    board_request = json.dumps({
        "name": "Sprint 1 - Authentication",
        "description": "Implement user authentication and authorization",
        "team_id": dev_team_id
    })
    board_response = board_api.create_board(board_request)
    board_id = json.loads(board_response)['id']
    print(f"   Request: {board_request}")
    print(f"   Response: {board_response}")
    
    # 2. Add Tasks
    print("\n2. Adding tasks using add_task() API:")
    
    # Task 1
    task1_request = json.dumps({
        "title": "Design authentication schema",
        "description": "Create database schema for user authentication",
        "user_id": alice_id,
        "board_id": board_id
    })
    task1_response = board_api.add_task(task1_request)
    task1_id = json.loads(task1_response)['id']
    print(f"   Request: {task1_request}")
    print(f"   Response: {task1_response}")
    
    # Task 2
    task2_request = json.dumps({
        "title": "Implement login endpoint",
        "description": "Create REST API endpoint for user login",
        "user_id": bob_id,
        "board_id": board_id
    })
    task2_response = board_api.add_task(task2_request)
    task2_id = json.loads(task2_response)['id']
    print(f"   Request: {task2_request}")
    print(f"   Response: {task2_response}")
    
    # Task 3
    task3_request = json.dumps({
        "title": "Add password hashing",
        "description": "Implement secure password hashing using bcrypt",
        "user_id": alice_id,
        "board_id": board_id
    })
    task3_response = board_api.add_task(task3_request)
    task3_id = json.loads(task3_response)['id']
    print(f"   Request: {task3_request}")
    print(f"   Response: {task3_response}")
    
    # 3. Update Task Status
    print("\n3. Updating task status using update_task_status() API:")
    
    # Update task 1 to IN_PROGRESS
    status_update1 = json.dumps({
        "id": task1_id,
        "status": "IN_PROGRESS"
    })
    status_response1 = board_api.update_task_status(status_update1)
    print(f"   Request: {status_update1}")
    print(f"   Response: {status_response1}")
    
    # Update task 2 to IN_PROGRESS
    status_update2 = json.dumps({
        "id": task2_id,
        "status": "IN_PROGRESS"
    })
    board_api.update_task_status(status_update2)
    
    # Complete task 1
    status_update3 = json.dumps({
        "id": task1_id,
        "status": "COMPLETE"
    })
    status_response3 = board_api.update_task_status(status_update3)
    print(f"   Request: {status_update3}")
    print(f"   Response: {status_response3}")
    
    # 4. List Boards
    print("\n4. Listing team boards using list_boards() API:")
    list_boards_request = json.dumps({"id": dev_team_id})
    list_boards_response = board_api.list_boards(list_boards_request)
    print(f"   Request: {list_boards_request}")
    print(f"   Response: {list_boards_response}")
    
    # 5. Export Board
    print("\n5. Exporting board using export_board() API:")
    export_request = json.dumps({"id": board_id})
    export_response = board_api.export_board(export_request)
    print(f"   Request: {export_request}")
    print(f"   Response: {export_response}")
    
    # 6. Close Board (will fail because not all tasks are complete)
    print("\n6. Attempting to close board using close_board() API:")
    print("   (This should fail because not all tasks are complete)")
    try:
        close_request = json.dumps({"id": board_id})
        close_response = board_api.close_board(close_request)
        print(f"   Request: {close_request}")
        print(f"   Response: {close_response}")
    except Exception as e:
        print(f"   Request: {close_request}")
        print(f"   Error (expected): {type(e).__name__}: {str(e)}")
    
    # Complete all tasks first
    print("\n   Completing remaining tasks...")
    board_api.update_task_status(json.dumps({"id": task2_id, "status": "COMPLETE"}))
    board_api.update_task_status(json.dumps({"id": task3_id, "status": "COMPLETE"}))
    
    # Now close the board
    print("\n   Trying again after completing all tasks:")
    close_response = board_api.close_board(close_request)
    print(f"   Response: {close_response}")
    
    # ========== ERROR HANDLING EXAMPLES ==========
    print_section("ERROR HANDLING EXAMPLES")
    
    print("\n1. Creating user with duplicate name:")
    try:
        duplicate_request = json.dumps({
            "name": "alice_cooper",
            "display_name": "Another Alice"
        })
        user_api.create_user(duplicate_request)
    except Exception as e:
        print(f"   Error (expected): {type(e).__name__}: {str(e)}")
    
    print("\n2. Creating team with non-existent admin:")
    try:
        invalid_team = json.dumps({
            "name": "Invalid Team",
            "description": "This should fail",
            "admin": "non-existent-id"
        })
        team_api.create_team(invalid_team)
    except Exception as e:
        print(f"   Error (expected): {type(e).__name__}: {str(e)}")
    
    print("\n3. Adding task to closed board:")
    try:
        invalid_task = json.dumps({
            "title": "This should fail",
            "description": "Cannot add to closed board",
            "user_id": alice_id,
            "board_id": board_id
        })
        board_api.add_task(invalid_task)
    except Exception as e:
        print(f"   Error (expected): {type(e).__name__}: {str(e)}")
    
    print("\n" + "="*60)
    print(" DEMO COMPLETE!")
    print("="*60)
    print("\nCheck the 'out' folder for the exported board file!")
    print("Check the 'db' folder to see the JSON files (but don't modify them!)")

if __name__ == "__main__":
    demo()