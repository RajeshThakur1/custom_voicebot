#!/usr/bin/env python3
"""
Test script for OTP-based Login System API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_send_otp(phone_number):
    """Test sending OTP"""
    print(f"\n📱 Testing OTP sending to {phone_number}...")
    try:
        payload = {"phone": phone_number}
        response = requests.post(
            f"{BASE_URL}/send-otp",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OTP sent successfully")
            print(f"   Message: {result['message']}")
            return True
        else:
            print(f"❌ Failed to send OTP: {response.status_code}")
            if response.headers.get('content-type') == 'application/json':
                print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Send OTP error: {e}")
        return False

def test_verify_otp(phone_number, otp):
    """Test OTP verification"""
    print(f"\n🔐 Testing OTP verification for {phone_number} with OTP: {otp}...")
    try:
        payload = {"phone": phone_number, "otp": otp}
        response = requests.post(
            f"{BASE_URL}/verify-otp",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OTP verified successfully")
            print(f"   Message: {result['message']}")
            return True
        else:
            print(f"❌ OTP verification failed: {response.status_code}")
            if response.headers.get('content-type') == 'application/json':
                print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Verify OTP error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Starting API tests for OTP-based Login System\n")
    
    # Test health check
    if not test_health_check():
        print("\n❌ Server is not responding. Please start the server first:")
        print("   python main.py")
        return
    
    # Test phone number validation
    test_phones = [
        "+919876543210",  # Valid format
        "9876543210",     # Valid format without country code
        "919876543210",   # Valid format with country code
        "+91 98765 43210", # Valid format with spaces
        "1234567890",     # Invalid (doesn't start with 6-9)
        "98765432",       # Invalid (too short)
    ]
    
    print("\n📋 Testing phone number validation:")
    for phone in test_phones:
        print(f"   Testing: {phone}")
        test_send_otp(phone)
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "="*60)
    print("🎯 MANUAL TESTING INSTRUCTIONS:")
    print("="*60)
    print("1. Start the server: python main.py")
    print("2. Open your browser: http://localhost:8000")
    print("3. Enter your real Indian phone number")
    print("4. Check your phone for the OTP SMS")
    print("5. Enter the received OTP")
    print("6. Verify the success message")
    print("\n🔧 For development testing with a real phone number:")
    print("   - Make sure your 2factor.in account has balance")
    print("   - Use a valid Indian mobile number")
    print("   - The OTP will arrive within 30-60 seconds")

if __name__ == "__main__":
    main()
