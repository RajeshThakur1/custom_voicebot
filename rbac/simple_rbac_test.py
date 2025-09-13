#!/usr/bin/env python3
"""
Simple RBAC System Test Script
Tests the Role-Based Access Control system with fresh users
"""

import requests
import json
import time
from typing import Dict, Any

class SimpleRBACTester:
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
            
    def create_test_user(self, username: str, email: str, password: str, role: str = "user") -> Dict[str, Any]:
        """Create a test user"""
        user_data = {
            "username": username,
            "email": email,
            "name": f"Test {username}",
            "password": password,
            "role": role
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/", json=user_data)
            if response.status_code == 201:
                print(f"✅ Created user: {username} with role: {role}")
                return {"username": username, "role": role}
            else:
                print(f"❌ Failed to create user {username}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating user {username}: {str(e)}")
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
                print(f"✅ Logged in user: {username}")
                return token
            else:
                print(f"❌ Failed to login user {username}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error logging in user {username}: {str(e)}")
            return None
    
    def test_todo_operations(self, username: str, token: str) -> bool:
        """Test todo operations for a specific user"""
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
                print(f"✅ Created todo for {username}: {created_todo['id']}")
                return True
            else:
                print(f"❌ Failed to create todo for {username}: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating todo for {username}: {str(e)}")
            return False
    
    def test_admin_access(self, admin_token: str) -> bool:
        """Test admin-specific functionality"""
        self.session.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        try:
            response = self.session.get(f"{self.base_url}/admin/todos")
            if response.status_code == 200:
                todos = response.json()
                print(f"✅ Admin can access all todos: {len(todos)} found")
                return True
            else:
                print(f"❌ Admin cannot access all todos: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing admin access: {str(e)}")
            return False
    
    def test_unauthorized_access(self, user_token: str) -> bool:
        """Test that non-admin users cannot access admin endpoints"""
        self.session.headers.update({"Authorization": f"Bearer {user_token}"})
        
        try:
            response = self.session.get(f"{self.base_url}/admin/todos")
            if response.status_code == 403:
                print(f"✅ Regular user correctly denied admin access")
                return True
            else:
                print(f"❌ Regular user unexpectedly got access: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing unauthorized access: {str(e)}")
            return False
    
    def test_user_profile(self, username: str, token: str) -> bool:
        """Test user profile access"""
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        try:
            response = self.session.get(f"{self.base_url}/user/")
            if response.status_code == 200:
                user_profile = response.json()
                print(f"✅ User profile accessed for {username}: {user_profile.get('username')}")
                return True
            else:
                print(f"❌ Failed to access user profile: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error accessing user profile: {str(e)}")
            return False
    
    def run_simple_test(self):
        """Run a simple RBAC test"""
        print("🚀 Starting Simple RBAC System Test")
        print(f"Target URL: {self.base_url}")
        
        # Test 1: Server Health
        self.print_test_header("Server Health Check")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.print_result("Server Health", True, f"Server is running: {response.json()}")
            else:
                self.print_result("Server Health", False, f"Status code: {response.status_code}")
                return
        except Exception as e:
            self.print_result("Server Health", False, f"Connection error: {str(e)}")
            return
        
        # Test 2: Create Users
        self.print_test_header("User Creation")
        test_users = [
            {"username": "admin_test", "email": "admin@test.com", "password": "admin123", "role": "admin"},
            {"username": "user_test", "email": "user@test.com", "password": "user123", "role": "user"},
            {"username": "manager_test", "email": "manager@test.com", "password": "manager123", "role": "manager"}
        ]
        
        for user_data in test_users:
            user = self.create_test_user(**user_data)
            if user:
                self.test_users[user_data["username"]] = user
        
        # Test 3: Login Users
        self.print_test_header("User Login")
        for user_data in test_users:
            token = self.login_user(user_data["username"], user_data["password"])
            if token:
                self.test_users[user_data["username"]]["token"] = token
        
        # Test 4: Todo Operations
        self.print_test_header("Todo Operations")
        for username in self.test_users:
            if "token" in self.test_users[username]:
                self.test_todo_operations(username, self.test_users[username]["token"])
        
        # Test 5: Admin Access Control
        self.print_test_header("Admin Access Control")
        if "admin_test" in self.test_users and "token" in self.test_users["admin_test"]:
            self.test_admin_access(self.test_users["admin_test"]["token"])
        
        # Test 6: Unauthorized Access Control
        self.print_test_header("Unauthorized Access Control")
        if "user_test" in self.test_users and "token" in self.test_users["user_test"]:
            self.test_unauthorized_access(self.test_users["user_test"]["token"])
        
        # Test 7: User Profile Access
        self.print_test_header("User Profile Access")
        for username in self.test_users:
            if "token" in self.test_users[username]:
                self.test_user_profile(username, self.test_users[username]["token"])
        
        # Test 8: Invalid Token
        self.print_test_header("Invalid Token Handling")
        self.session.headers.update({"Authorization": "Bearer invalid_token_123"})
        try:
            response = self.session.get(f"{self.base_url}/todos/")
            if response.status_code == 401:
                print("✅ Invalid token correctly rejected")
            else:
                print(f"❌ Invalid token not rejected: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing invalid token: {str(e)}")
        
        print(f"\n{'='*60}")
        print("RBAC TEST COMPLETED")
        print(f"{'='*60}")
        print("Summary:")
        print(f"- Users created: {len([u for u in self.test_users.values() if u])}")
        print(f"- Users logged in: {len([u for u in self.test_users.values() if 'token' in u])}")
        print(f"- Todos created: {len(self.test_todos)}")

def main():
    """Main function to run the simple RBAC test"""
    tester = SimpleRBACTester()
    tester.run_simple_test()

if __name__ == "__main__":
    main() 