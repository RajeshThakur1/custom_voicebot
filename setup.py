#!/usr/bin/env python3
"""
Setup script for OTP-based Login System
This script helps set up the virtual environment and install dependencies
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up OTP-based Login System...")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  No virtual environment detected. Creating one...")
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            return False
        
        print("\n📝 To activate the virtual environment, run:")
        print("   source venv/bin/activate  (on macOS/Linux)")
        print("   venv\\Scripts\\activate     (on Windows)")
        print("\nThen run this setup script again.")
        return True
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Check if API.env exists
    if os.path.exists("API.env"):
        print("✅ API.env file found")
    else:
        print("⚠️  API.env file not found. Creating template...")
        with open("API.env", "w") as f:
            f.write("API=your_2factor_api_key_here\n")
        print("📝 Please update API.env with your 2factor.in API key")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Make sure your 2factor.in API key is set in API.env")
    print("2. Run the application: python main.py")
    print("3. Open your browser and go to: http://localhost:8000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
