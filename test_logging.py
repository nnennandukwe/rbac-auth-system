#!/usr/bin/env python3
"""
Test script to demonstrate the logging functionality of the RBAC Auth System.
This script makes various API calls to generate different types of log entries.
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def make_request(method: str, endpoint: str, data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> requests.Response:
    """Make an HTTP request and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    if method.upper() == "GET":
        return requests.get(url, headers=headers)
    elif method.upper() == "POST":
        return requests.post(url, json=data, headers=headers)
    else:
        raise ValueError(f"Unsupported method: {method}")

def test_registration():
    """Test user registration - generates registration logs"""
    print("\\n=== Testing User Registration ===")
    
    # Successful registration
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "testpass123",
        "role_names": ["Viewer"]
    }
    
    response = make_request("POST", "/auth/register", user_data)
    print(f"Registration response: {response.status_code}")
    if response.status_code == 200:
        print(f"User created: {response.json()}")
    else:
        print(f"Registration failed: {response.text}")
    
    # Duplicate registration (should fail)
    response = make_request("POST", "/auth/register", user_data)
    print(f"Duplicate registration response: {response.status_code}")

def test_login():
    """Test user login - generates authentication logs"""
    print("\\n=== Testing User Login ===")
    
    # Successful login with admin user
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = make_request("POST", "/auth/login", login_data)
    print(f"Admin login response: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"Login successful, token received")
        return token_data["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None
    
    # Failed login attempt
    bad_login_data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    response = make_request("POST", "/auth/login", bad_login_data)
    print(f"Bad login response: {response.status_code}")

def test_protected_routes(token: str):
    """Test protected routes - generates authorization logs"""
    print("\\n=== Testing Protected Routes ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test admin route (should succeed for admin user)
    response = make_request("GET", "/admin", headers=headers)
    print(f"Admin route response: {response.status_code}")
    if response.status_code == 200:
        print(f"Admin access: {response.json()}")
    
    # Test editor route (should succeed for admin user)
    response = make_request("GET", "/edit", headers=headers)
    print(f"Editor route response: {response.status_code}")
    if response.status_code == 200:
        print(f"Editor access: {response.json()}")
    
    # Test viewer route (should succeed for admin user)
    response = make_request("GET", "/view", headers=headers)
    print(f"Viewer route response: {response.status_code}")
    if response.status_code == 200:
        print(f"Viewer access: {response.json()}")

def test_unauthorized_access():
    """Test unauthorized access - generates security violation logs"""
    print("\\n=== Testing Unauthorized Access ===")
    
    # Access protected route without token
    response = make_request("GET", "/admin")
    print(f"No token admin access: {response.status_code}")
    
    # Access with invalid token
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = make_request("GET", "/admin", headers=headers)
    print(f"Invalid token admin access: {response.status_code}")

def test_limited_user():
    """Test limited user access - generates permission denial logs"""
    print("\\n=== Testing Limited User Access ===")
    
    # First, login with the test user (viewer only)
    login_data = {
        "username": "test_user",
        "password": "testpass123"
    }
    
    response = make_request("POST", "/auth/login", login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test viewer route (should succeed)
        response = make_request("GET", "/view", headers=headers)
        print(f"Test user viewer access: {response.status_code}")
        
        # Test editor route (should fail - permission denied)
        response = make_request("GET", "/edit", headers=headers)
        print(f"Test user editor access: {response.status_code}")
        
        # Test admin route (should fail - permission denied)
        response = make_request("GET", "/admin", headers=headers)
        print(f"Test user admin access: {response.status_code}")
    else:
        print("Could not login with test user")

def main():
    """Main test function"""
    print("RBAC Auth System Logging Test")
    print("=" * 40)
    print("This script will generate various log entries to demonstrate the logging system.")
    print("Make sure the server is running on http://localhost:8000")
    print("Check the logs/ directory for generated log files.")
    
    try:
        # Test basic connectivity
        response = make_request("GET", "/")
        if response.status_code != 200:
            print("Server not responding. Make sure it's running on http://localhost:8000")
            return
        
        print(f"Server is running: {response.json()}")
        
        # Run tests
        test_registration()
        time.sleep(1)  # Small delay between tests
        
        token = test_login()
        time.sleep(1)
        
        if token:
            test_protected_routes(token)
            time.sleep(1)
        
        test_unauthorized_access()
        time.sleep(1)
        
        test_limited_user()
        
        print("\\n=== Test Complete ===")
        print("Check the following log files:")
        print("- logs/rbac_auth.log (application logs)")
        print("- logs/security.log (security events)")
        print("- logs/audit.log (audit events)")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main()