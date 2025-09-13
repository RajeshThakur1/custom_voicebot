#!/usr/bin/env python3
"""
Final RBAC System Test Script
Comprehensive testing of the Role-Based Access Control system
"""

import requests
import json
import time
from typing import Dict, Any

class FinalRBACTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {}
        
    def print_header(self, title: str):
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        
    def print_result(self, test_name: str, success: bool, details: str = ""):
        status = "PASS" if success else "FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
        self.results[test_name] = success
        
    def test_server_health(self):
        """Test if the server is running"""
        self.print_header("1. SERVER HEALTH CHECK")
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
    
    def test_user_creation(self):
        """Test user creation with different roles"""
        self.print_header("2. USER CREATION TEST")
        
        test_users = [
            {"username": "test_admin", "email": "admin@test.com", "name": "Test Admin", "password": "admin123", "role": "admin"},
            {"username": "test_user", "email": "user@test.com", "name": "Test User", "password": "user123", "role": "user"},
            {"username": "test_manager", "email": "manager@test.com", "name": "Test Manager", "password": "manager123", "role": "manager"}
        ]
        
        created_users = {}
        for user_data in test_users:
            try:
                response = self.session.post(f"{self.base_url}/auth/", json=user_data)
                if response.status_code == 201:
                    created_users[user_data["username"]] = user_data
                    self.print_result(f"Create {user_data['role']} user", True, f"Created: {user_data['username']}")
                else:
                    self.print_result(f"Create {user_data['role']} user", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_result(f"Create {user_data['role']} user", False, f"Error: {str(e)}")
        
        return created_users
    
    def test_user_login(self, users):
        """Test user login and token generation"""
        self.print_header("3. USER LOGIN TEST")
        
        logged_in_users = {}
        for username, user_data in users.items():
            try:
                login_data = {
                    "username": username,
                    "password": user_data["password"]
                }
                response = self.session.post(f"{self.base_url}/auth/login", data=login_data)
                if response.status_code == 200:
                    token_data = response.json()
                    logged_in_users[username] = {
                        **user_data,
                        "token": token_data["access_token"]
                    }
                    self.print_result(f"Login {user_data['role']} user", True, f"Logged in: {username}")
                else:
                    self.print_result(f"Login {user_data['role']} user", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_result(f"Login {user_data['role']} user", False, f"Error: {str(e)}")
        
        return logged_in_users
    
    def test_todo_operations(self, users):
        """Test todo operations for each user"""
        self.print_header("4. TODO OPERATIONS TEST")
        
        created_todos = {}
        for username, user_data in users.items():
            if "token" not in user_data:
                continue
                
            # Set authorization header
            headers = {"Authorization": f"Bearer {user_data['token']}"}
            
            # Test create todo
            todo_data = {
                "title": f"Todo for {username}",
                "description": f"Test todo for {username}",
                "priority": 3,
                "complete": False
            }
            
            try:
                response = self.session.post(f"{self.base_url}/todos/", json=todo_data, headers=headers)
                if response.status_code == 200:
                    todo = response.json()
                    created_todos[username] = todo
                    self.print_result(f"Create todo for {user_data['role']}", True, f"Todo ID: {todo['id']}")
                else:
                    self.print_result(f"Create todo for {user_data['role']}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_result(f"Create todo for {user_data['role']}", False, f"Error: {str(e)}")
        
        return created_todos
    
    def test_admin_access_control(self, users):
        """Test admin access control"""
        self.print_header("5. ADMIN ACCESS CONTROL TEST")
        
        admin_user = None
        for username, user_data in users.items():
            if user_data.get("role") == "admin" and "token" in user_data:
                admin_user = user_data
                break
        
        if not admin_user:
            self.print_result("Admin Access Control", False, "No admin user found")
            return False
        
        # Test admin access to all todos
        headers = {"Authorization": f"Bearer {admin_user['token']}"}
        try:
            response = self.session.get(f"{self.base_url}/admin/todos", headers=headers)
            if response.status_code == 200:
                todos = response.json()
                self.print_result("Admin Access Control", True, f"Admin can access {len(todos)} todos")
                return True
            else:
                self.print_result("Admin Access Control", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Admin Access Control", False, f"Error: {str(e)}")
            return False
    
    def test_unauthorized_access(self, users):
        """Test that non-admin users cannot access admin endpoints"""
        self.print_header("6. UNAUTHORIZED ACCESS TEST")
        
        non_admin_user = None
        for username, user_data in users.items():
            if user_data.get("role") != "admin" and "token" in user_data:
                non_admin_user = user_data
                break
        
        if not non_admin_user:
            self.print_result("Unauthorized Access Control", False, "No non-admin user found")
            return False
        
        # Test that regular user cannot access admin endpoint
        headers = {"Authorization": f"Bearer {non_admin_user['token']}"}
        try:
            response = self.session.get(f"{self.base_url}/admin/todos", headers=headers)
            if response.status_code == 403:
                self.print_result("Unauthorized Access Control", True, "Correctly denied access")
                return True
            else:
                self.print_result("Unauthorized Access Control", False, f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Unauthorized Access Control", False, f"Error: {str(e)}")
            return False
    
    def test_user_profile_access(self, users):
        """Test user profile access"""
        self.print_header("7. USER PROFILE ACCESS TEST")
        
        success_count = 0
        for username, user_data in users.items():
            if "token" not in user_data:
                continue
                
            headers = {"Authorization": f"Bearer {user_data['token']}"}
            try:
                response = self.session.get(f"{self.base_url}/user/", headers=headers)
                if response.status_code == 200:
                    profile = response.json()
                    self.print_result(f"Profile access for {user_data['role']}", True, f"Username: {profile.get('username')}")
                    success_count += 1
                else:
                    self.print_result(f"Profile access for {user_data['role']}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.print_result(f"Profile access for {user_data['role']}", False, f"Error: {str(e)}")
        
        return success_count > 0
    
    def test_invalid_token(self):
        """Test invalid token handling"""
        self.print_header("8. INVALID TOKEN TEST")
        
        headers = {"Authorization": "Bearer invalid_token_123"}
        try:
            response = self.session.get(f"{self.base_url}/todos/", headers=headers)
            if response.status_code == 401:
                self.print_result("Invalid Token Handling", True, "Correctly rejected invalid token")
                return True
            else:
                self.print_result("Invalid Token Handling", False, f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Invalid Token Handling", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all RBAC tests"""
        print("STARTING COMPREHENSIVE RBAC SYSTEM TEST")
        print(f"Target URL: {self.base_url}")
        
        # Test 1: Server Health
        if not self.test_server_health():
            print("\nServer is not running. Cannot proceed with tests.")
            return
        
        # Test 2: User Creation
        users = self.test_user_creation()
        
        # Test 3: User Login
        logged_in_users = self.test_user_login(users)
        
        # Test 4: Todo Operations
        todos = self.test_todo_operations(logged_in_users)
        
        # Test 5: Admin Access Control
        self.test_admin_access_control(logged_in_users)
        
        # Test 6: Unauthorized Access Control
        self.test_unauthorized_access(logged_in_users)
        
        # Test 7: User Profile Access
        self.test_user_profile_access(logged_in_users)
        
        # Test 8: Invalid Token
        self.test_invalid_token()
        
        # Print final summary
        self.print_header("FINAL TEST SUMMARY")
        
        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print(f"\nDetailed Results:")
        for test_name, result in self.results.items():
            status = "PASS" if result else "FAIL"
            print(f"  {status} - {test_name}")
        
        print(f"\nRBAC System Status:")
        if success_rate >= 80:
            print("EXCELLENT - RBAC system is working correctly!")
        elif success_rate >= 60:
            print("GOOD - RBAC system is mostly working with some issues")
        else:
            print("POOR - RBAC system has significant issues")
        
        return success_rate

def main():
    """Main function to run the comprehensive RBAC test"""
    tester = FinalRBACTester()
    success_rate = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if success_rate >= 80:
        print("\nRBAC system test completed successfully!")
        exit(0)
    else:
        print("\nRBAC system test completed with issues.")
        exit(1)

if __name__ == "__main__":
    main() 