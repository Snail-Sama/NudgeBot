# import requests


# def run_smoketest():
#     base_url = "http://localhost:5000/api"
#     username = "test"
#     password = "test"


#     goal_biceps = {
#         "target": "biceps",
#         "goal_value": 40,
#         "goal_progress": 35.0,
#         "completed": False,
#         "progress_notes": "[]"
#     }

#     updated_biceps = {
#         "target": "biceps",
#         "goal_value": 40,
#         "goal_progress": 40.0,
#         "completed": True,
#         "progress_notes": "[]"
#     }

#     goal_pecs = {
#         "target": "pectorals",
#         "goal_value": 200,
#         "goal_progress": 225.0,
#         "completed": True,
#         "progress_ntoes": "[]"
#     }

#     example_workout = {
#         "amount": 25.0,
#         "exercise_type": "Push-up",
#         "duration": 30,
#         "intensity": "High",
#         "note": ""
#     }

#     health_response = requests.get(f"{base_url}/health")
#     assert health_response.status_code == 200
#     assert health_response.json()["status"] == "success"

#     delete_user_response = requests.delete(f"{base_url}/reset-users")
#     assert delete_user_response.status_code == 200
#     assert delete_user_response.json()["status"] == "success"
#     print("Reset users successful")

#     delete_goal_response = requests.delete(f"{base_url}/reset-goals")
#     assert delete_goal_response.status_code == 200
#     assert delete_goal_response.json()["status"] == "success"
#     print("Reset goal successful")

#     create_user_response = requests.put(f"{base_url}/create-user", json={
#         "username": username,
#         "password": password
#     })
#     assert create_user_response.status_code == 201
#     assert create_user_response.json()["status"] == "success"
#     print("User creation successful")

#     session = requests.Session()

#     # Log in
#     login_resp = session.post(f"{base_url}/login", json={
#         "username": username,
#         "password": password
#     })
#     assert login_resp.status_code == 200
#     assert login_resp.json()["status"] == "success"
#     print("Login successful")

#     biceps_id = 1
#     create_biceps_resp = session.post(f"{base_url}/create-goal", json=goal_biceps)
#     assert create_biceps_resp.status_code == 201
#     assert create_biceps_resp.json()["status"] == "success"
#     print("Boxer creation successful")

#     # Change password
#     change_password_resp = session.post(f"{base_url}/change-password", json={
#         "new_password": "new_password"
#     })
#     assert change_password_resp.status_code == 200
#     assert change_password_resp.json()["status"] == "success"
#     print("Password change successful")

#     # Log in with new password
#     login_resp = session.post(f"{base_url}/login", json={
#         "username": username,
#         "password": "new_password"
#     })
#     assert login_resp.status_code == 200
#     assert login_resp.json()["status"] == "success"
#     print("Login with new password successful")


#     pecs_id = 2
#     create_pecs_resp = session.post(f"{base_url}/create-goal", json=goal_pecs)
#     assert create_pecs_resp.status_code == 201
#     assert create_pecs_resp.json()["status"] == "success"
#     print("goal creation successful")


#     get_goal_by_id_resp = session.get(f"{base_url}/get-goal-from-catalog-by-id/{biceps_id}")
#     assert get_goal_by_id_resp.status_code == 200
#     assert get_goal_by_id_resp.json()["target"] == "biceps"
#     assert get_goal_by_id_resp.json()["status"] == "success"
#     print("goal retrieved successfully")


#     add_goal_to_plan_resp = session.post(f"{base_url}/add-goal-to-plan/{biceps_id}")
#     assert add_goal_to_plan_resp.status_code == 200
#     assert add_goal_to_plan_resp.json()["status"] == "success"
#     assert add_goal_to_plan_resp.json()["message"] == "goal biceps - 35.0 out of 40 added to plan"
#     print("goal added to plan successfully")


#     get_rec_resp = session.get(f"{base_url}/goals/recommendations/{pecs_id}")
#     assert get_rec_resp.status_code == 200
#     assert get_rec_resp.json()["status"] == "success"
#     assert get_rec_resp.json()["recommendations"] == [{'bodyPart': 'chest', 'equipment': 'leverage machine', 'gifUrl': 'https://v2.exercisedb.io/image/M1vEH1gTLk2nxf', 'id': '0009', 'name': 'assisted chest dip (kneeling)', 'target': 'pectorals', 'secondaryMuscles': ['triceps', 'shoulders'], 'instructions': ['Adjust the machine to your desired height and secure your knees on the pad.', 'Grasp the handles with your palms facing down and your arms fully extended.', 'Lower your body by bending your elbows until your upper arms are parallel to the floor.', 'Pause for a moment, then push yourself back up to the starting position.', 'Repeat for the desired number of repetitions.']}]
#     print("recommendation retrieved successfully")

#     log_workout_resp = session.post(f"{base_url}/goals/log-session/{pecs_id}", json=example_workout)
#     assert log_workout_resp.status_code == 200
#     assert log_workout_resp.json()["status"] == "success"
#     assert log_workout_resp.json()["message"] == "Goal completed! Total progress: 125.0%"
#     print("workout logged successfully")


#     get_all_goals_from_plan_resp = session.get(f"{base_url}/get-all-goals-from-plan")
#     assert get_all_goals_from_plan_resp.status_code == 200
#     assert get_all_goals_from_plan_resp.json()["status"] == "success"
#     assert get_all_goals_from_plan_resp.json()["goals"] == [biceps_id]
#     print("plan retrieved successfully")


#     get_plan_progress_resp = session.get(f"{base_url}/get-plan-progress")
#     assert get_plan_progress_resp.status_code == 200
#     assert get_plan_progress_resp.json()["status"] == "success"
#     assert get_plan_progress_resp.json()["percentage"] == 0.0
#     print("plan progress retrieved successfully")


#     remove_goal_from_plan_resp = session.delete(f"{base_url}/remove-goal-from-plan/{biceps_id}")
#     assert remove_goal_from_plan_resp.status_code == 200
#     assert remove_goal_from_plan_resp.json()["status"] == "success"
#     assert remove_goal_from_plan_resp.json()["message"] == f"Goal with id {biceps_id} removed from plan"
#     print("goal removed from plan successfully")


#     clear_plan_resp = session.post(f"{base_url}/clear-plan")
#     assert clear_plan_resp.status_code == 200
#     assert clear_plan_resp.json()["status"] == "success"
#     print("plan cleared successfully")

#     get_goal_by_target_resp = session.get(f"{base_url}/goals/by-target/{goal_biceps["target"]}")
#     assert get_goal_by_target_resp.status_code == 200
#     assert get_goal_by_target_resp.json()["goals"] == [biceps_id]
#     assert get_goal_by_target_resp.json()["status"] == "success"
#     print("goal retrieved successfully")


#     get_goal_by_completed_resp = session.get(f"{base_url}/goals/by-completed/{goal_pecs["completed"]}")
#     assert get_goal_by_completed_resp.status_code == 200
#     assert get_goal_by_completed_resp.json()["goals"] == [pecs_id]
#     assert get_goal_by_completed_resp.json()["status"] == "success"
#     print("goal retrieved successfully")


#     get_goal_by_value_resp = session.get(f"{base_url}/goals/by-value/{goal_pecs["goal_value"]}")
#     assert get_goal_by_value_resp.status_code == 200
#     assert get_goal_by_value_resp.json()["goals"] == [pecs_id]
#     assert get_goal_by_value_resp.json()["status"] == "success"
#     print("goal retrieved successfully")


#     update_goal_resp = session.patch(f"{base_url}/update-goal/{biceps_id}", json=updated_biceps)
#     assert update_goal_resp.status_code == 200
#     assert update_goal_resp.json()["status"] == "success"
#     assert update_goal_resp.json()["updated_fields"] == [updated_biceps["goal_progress"], updated_biceps["completed"]]
#     print("goal updated successfully")

    
#     get_all_goals_resp = session.get(f"{base_url}/get-all-goals-from-catalog")
#     assert get_all_goals_resp.status_code == 200
#     assert [get_all_goals_resp.json()["goals"][0]["id"],get_all_goals_resp.json()["goals"][1]["id"]] == [biceps_id, pecs_id]
#     assert get_all_goals_resp.json()["status"] == "success"
#     print("goals retrieved successfully")


#     delete_pecs_resp = session.delete(f"{base_url}/delete-goal/{pecs_id}")
#     assert delete_pecs_resp.status_code == 200
#     assert delete_pecs_resp.json()["status"] == "success"
#     print("goal deletion successful")


#     fake_id = 3
#     delete_fake_resp = session.delete(f"{base_url}/delete-goal/{fake_id}")
#     assert delete_fake_resp.status_code == 500
#     assert delete_fake_resp.json()["status"] == "error"
#     print("goal deletion failed as expected")

#     # Log out
#     logout_resp = session.post(f"{base_url}/logout")
#     assert logout_resp.status_code == 200
#     assert logout_resp.json()["status"] == "success"
#     print("Logout successful")

#     create_boxer_logged_out_resp = session.post(f"{base_url}/create-goal", json=goal_pecs)
#     # This should fail because we are logged out
#     assert create_boxer_logged_out_resp.status_code == 401
#     assert create_boxer_logged_out_resp.json()["status"] == "error"
#     print("goal creation failed as expected")

# if __name__ == "__main__":
#     run_smoketest()
