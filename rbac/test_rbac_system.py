"""
Comprehensive RBAC System Test Script
Tests the Role-Based Access Control system with different user roles and permissions
"""

import requests
import json
import time
from typing import Dict, Any

class RBACTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_users = {}
        self.test_todos = {}
        
    def print_test_header(self, test_name: str):
        print(f"\n{'='*60}")
        print(f"TESTING: {test_name}")
        print(f"{'='*60}")
        
    def print_result(self, test_name: str, success: bool, details: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
            
    def test_server_health(self) -> bool:
        """Test if the server is running"""
        self.print_test_header("Server Health Check")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.print_result("Server Health", True, f"Server is running: {response.json()}")
                return True
            else:
                self.print_result("Server Health", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Server Health", False, f"Connection error: {str(e)}")
            return False
    
    def create_test_user(self, username: str, email: str, password: str, role: str = "user") -> Dict[str, Any]:
        """Create a test user"""
        user_data = {
            "username": username,
            "email": email,
            "name": f"Test{username.capitalize()} User",
            "password": password,
            "role": role
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/", json=user_data)
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Failed to create user {username}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error creating user {username}: {str(e)}")
            return None
    
    def login_user(self, username: str, password: str) -> str:
        """Login user and return access token"""
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/login", data=login_data)
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                return token
            else:
                print(f"Failed to login user {username}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error logging in user {username}: {str(e)}")
            return None
    
    def test_user_registration_and_login(self) -> bool:
        """Test user registration and login functionality"""
        self.print_test_header("User Registration and Login")
        
        # Test user registration
        test_users = [
            {"username": "admin_user", "email": "admin@test.com", "password": "admin123", "role": "admin"},
            {"username": "regular_user", "email": "user@test.com", "password": "user123", "role": "user"},
            {"username": "manager_user", "email": "manager@test.com", "password": "manager123", "role": "manager"}
        ]
        
        success_count = 0
        for user_data in test_users:
            user = self.create_test_user(**user_data)
            if user:
                self.test_users[user_data["username"]] = user
                success_count += 1
                self.print_result(f"Create User: {user_data['username']}", True, f"Role: {user_data['role']}")
            else:
                self.print_result(f"Create User: {user_data['username']}", False)
        
        # Test user login
        login_success_count = 0
        for user_data in test_users:
            if user_data["username"] in self.test_users:  # Only try to login if user was created
                token = self.login_user(user_data["username"], user_data["password"])
                if token:
                    self.test_users[user_data["username"]]["token"] = token
                    login_success_count += 1
                    self.print_result(f"Login User: {user_data['username']}", True)
                else:
                    self.print_result(f"Login User: {user_data['username']}", False)
            else:
                self.print_result(f"Login User: {user_data['username']}", False, "User not created")
        
        return success_count == len(test_users) and login_success_count == len(test_users)
    
    def test_todo_operations(self, username: str) -> bool:
        """Test todo operations for a specific user"""
        self.print_test_header(f"Todo Operations for {username}")
        
        if username not in self.test_users:
            self.print_result(f"Todo Operations: {username}", False, "User not found")
            return False
        
        # Set the user's token
        token = self.test_users[username]["token"]
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Test create todo
        todo_data = {
            "title": f"Test Todo for {username}",
            "description": f"This is a test todo for {username}",
            "priority": 3,
            "complete": False
        }
        
        try:
            response = self.session.post(f"{self.base_url}/todos/", json=todo_data)
            if response.status_code == 200:
                created_todo = response.json()
                self.test_todos[username] = created_todo
                self.print_result(f"Create Todo: {username}", True, f"Todo ID: {created_todo['id']}")
            else:
                self.print_result(f"Create Todo: {username}", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_result(f"Create Todo: {username}", False, f"Error: {str(e)}")
            return False
        
        # Test get all todos
        try:
            response = self.session.get(f"{self.base_url}/todos/")
            if response.status_code == 200:
                todos = response.json()
                self.print_result(f"Get Todos: {username}", True, f"Found {len(todos)} todos")
            else:
                self.print_result(f"Get Todos: {username}", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_result(f"Get Todos: {username}", False, f"Error: {str(e)}")
            return False
        
        # Test get specific todo
        if username in self.test_todos:
            todo_id = self.test_todos[username]["id"]
            try:
                response = self.session.get(f"{self.base_url}/todos/todo/{todo_id}")
                if response.status_code == 200:
                    self.print_result(f"Get Todo {todo_id}: {username}", True)
                else:
                    self.print_result(f"Get Todo {todo_id}: {username}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_result(f"Get Todo {todo_id}: {username}", False, f"Error: {str(e)}")
        
        return True
    
    def test_admin_access(self) -> bool:
        """Test admin-specific functionality"""
        self.print_test_header("Admin Access Control")
        
        if "admin_user" not in self.test_users:
            self.print_result("Admin Access", False, "Admin user not found")
            return False
        
        # Set admin token
        admin_token = self.test_users["admin_user"]["token"]
        self.session.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        # Test admin access to all todos
        try:
            response = self.session.get(f"{self.base_url}/admin/todos")
            if response.status_code == 200:
                todos = response.json()
                self.print_result("Admin Get All Todos", True, f"Found {len(todos)} todos")
                return True
            else:
                self.print_result("Admin Get All Todos", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Admin Get All Todos", False, f"Error: {str(e)}")
            return False
    
    def test_unauthorized_access(self) -> bool:
        """Test that non-admin users cannot access admin endpoints"""
        self.print_test_header("Unauthorized Access Control")
        
        if "regular_user" not in self.test_users:
            self.print_result("Unauthorized Access", False, "Regular user not found")
            return False
        
        # Set regular user token
        user_token = self.test_users["regular_user"]["token"]
        self.session.headers.update({"Authorization": f"Bearer {user_token}"})
        
        # Test that regular user cannot access admin endpoint
        try:
            response = self.session.get(f"{self.base_url}/admin/todos")
            if response.status_code == 403:
                self.print_result("Regular User Admin Access Denied", True, "Correctly denied access")
                return True
            else:
                self.print_result("Regular User Admin Access Denied", False, f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Regular User Admin Access Denied", False, f"Error: {str(e)}")
            return False
    
    def test_user_isolation(self) -> bool:
        """Test that users can only access their own todos"""
        self.print_test_header("User Data Isolation")
        
        if "regular_user" not in self.test_users or "manager_user" not in self.test_users:
            self.print_result("User Isolation", False, "Test users not found")
            return False
        
        # Try to access another user's todo
        if "regular_user" in self.test_todos and "manager_user" in self.test_todos:
            regular_todo_id = self.test_todos["regular_user"]["id"]
            
            # Set manager token and try to access regular user's todo
            manager_token = self.test_users["manager_user"]["token"]
            self.session.headers.update({"Authorization": f"Bearer {manager_token}"})
            
            try:
                response = self.session.get(f"{self.base_url}/todos/todo/{regular_todo_id}")
                if response.status_code == 404:
                    self.print_result("User Data Isolation", True, "Correctly denied access to other user's todo")
                    return True
                else:
                    self.print_result("User Data Isolation", False, f"Unexpected status: {response.status_code}")
                    return False
            except Exception as e:
                self.print_result("User Data Isolation", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_invalid_token(self) -> bool:
        """Test access with invalid token"""
        self.print_test_header("Invalid Token Handling")
        
        # Set invalid token
        self.session.headers.update({"Authorization": "Bearer invalid_token_123"})
        
        try:
            response = self.session.get(f"{self.base_url}/todos/")
            if response.status_code == 401:
                self.print_result("Invalid Token Rejection", True, "Correctly rejected invalid token")
                return True
            else:
                self.print_result("Invalid Token Rejection", False, f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Invalid Token Rejection", False, f"Error: {str(e)}")
            return False
    
    def test_user_profile_access(self) -> bool:
        """Test user profile access"""
        self.print_test_header("User Profile Access")
        
        if "regular_user" not in self.test_users:
            self.print_result("User Profile Access", False, "Regular user not found")
            return False
        
        # Set regular user token
        user_token = self.test_users["regular_user"]["token"]
        self.session.headers.update({"Authorization": f"Bearer {user_token}"})
        
        try:
            response = self.session.get(f"{self.base_url}/user/")
            if response.status_code == 200:
                user_profile = response.json()
                self.print_result("User Profile Access", True, f"Username: {user_profile.get('username')}")
                return True
            else:
                self.print_result("User Profile Access", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("User Profile Access", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self) -> Dict[str, bool]:
        """Run all RBAC tests"""
        print("🚀 Starting Comprehensive RBAC System Test")
        print(f"Target URL: {self.base_url}")
        
        results = {}
        
        # Test 1: Server Health
        results["server_health"] = self.test_server_health()
        if not results["server_health"]:
            print("❌ Server is not running. Please start the FastAPI server first.")
            return results
        
        # Test 2: User Registration and Login
        results["user_registration_login"] = self.test_user_registration_and_login()
        
        # Test 3: Todo Operations for each user
        for username in ["admin_user", "regular_user", "manager_user"]:
            if username in self.test_users:
                results[f"todo_operations_{username}"] = self.test_todo_operations(username)
        
        # Test 4: Admin Access Control
        results["admin_access"] = self.test_admin_access()
        
        # Test 5: Unauthorized Access Control
        results["unauthorized_access"] = self.test_unauthorized_access()
        
        # Test 6: User Data Isolation
        results["user_isolation"] = self.test_user_isolation()
        
        # Test 7: Invalid Token Handling
        results["invalid_token"] = self.test_invalid_token()
        
        # Test 8: User Profile Access
        results["user_profile"] = self.test_user_profile_access()
        
        # Print summary
        self.print_test_header("Test Summary")
        passed = sum(results.values())
        total = len(results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        return results

def main():
    """Main function to run the RBAC tests"""
    tester = RBACTester()
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if all(results.values()):
        print("\n🎉 All tests passed! RBAC system is working correctly.")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
        exit(1)

if __name__ == "__main__":
    main() 