#!/usr/bin/env python3
"""
Simple script to run the OTP-based Login System
"""

import subprocess
import sys
import os

def main():
    """Main function to run the FastAPI application"""
    print("🚀 Starting OTP-based Login System...")
    
    # Check if API.env exists
    if not os.path.exists("API.env"):
        print("❌ API.env file not found!")
        print("Please create API.env file with your 2factor.in API key:")
        print("API=your_2factor_api_key_here")
        return False
    
    # Check if virtual environment is activated (optional)
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        print("⚠️  Virtual environment not detected. Consider activating it:")
        print("   source venv/bin/activate  (on macOS/Linux)")
        print("   venv\\Scripts\\activate     (on Windows)")
        print()
    
    try:
        print("🌐 Starting server at http://localhost:8000")
        print("📱 Open your browser and navigate to the above URL")
        print("🛑 Press Ctrl+C to stop the server")
        print()
        
        # Run the FastAPI application
        subprocess.run([sys.executable, "main.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running the application: {e}")
        return False
    except FileNotFoundError:
        print("\n❌ Python not found. Please check your Python installation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
