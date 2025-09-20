import os
from dotenv import load_dotenv
from typing import Dict, Optional
import re
import time
from pydantic import BaseModel, validator
import random
import requests
# Load environment variables
load_dotenv()

# app = FastAPI(title="OTP-based Login System", description="Complete OTP verification system using 2factor.in")

# Templates for HTML rendering
# templates = Jinja2Templates(directory="templates")

# In-memory storage for OTPs (in production, use Redis or database)
otp_storage: Dict[str, Dict] = {}


class PhoneNumber(BaseModel):
    phone: str

    @validator('phone')
    def validate_indian_phone(cls, v):
        # Remove any spaces, dashes, or special characters
        phone = re.sub(r'[^\d+]', '', v)

        # Check if it's a valid Indian phone number
        # Indian mobile numbers: +91 followed by 10 digits starting with 6-9
        if phone.startswith('+91'):
            phone = phone[3:]
        elif phone.startswith('91') and len(phone) == 12:
            phone = phone[2:]
        elif phone.startswith('0') and len(phone) == 11:
            phone = phone[1:]

        if not (len(phone) == 10 and phone[0] in '6789' and phone.isdigit()):
            raise ValueError('Invalid Indian phone number format')

        return '+91' + phone


class OTPVerification(BaseModel):
    phone: str
    otp: str

    @validator('otp')
    def validate_otp(cls, v):
        if not (v.isdigit() and len(v) == 6):
            raise ValueError('OTP must be a 6-digit number')
        return v


class OTPService:
    def __init__(self):
        self.api_key = os.getenv('API')
        if not self.api_key:
            raise ValueError("API key not found in environment variables")
        self.base_url = "https://2factor.in/API/V1"

    def generate_otp(self) -> str:
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))

    def send_otp(self, phone: str, otp: str) -> bool:
        """Send OTP via 2factor.in SMS API"""
        try:
            # Remove +91 prefix for the API call
            clean_phone = phone.replace('+91', '')

            url = f"{self.base_url}/{self.api_key}/SMS/{clean_phone}/{otp}/OTP1"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                result = response.json()
                return result.get('Status') == 'Success'
            return False
        except Exception as e:
            print(f"Error sending OTP: {e}")
            return False

    def store_otp(self, phone: str, otp: str):
        """Store OTP with timestamp for verification"""
        otp_storage[phone] = {
            'otp': otp,
            'timestamp': time.time(),
            'attempts': 0
        }

    def verify_otp(self, phone: str, user_otp: str) -> Dict[str, any]:
        """Verify OTP against stored value"""
        if phone not in otp_storage:
            return {'success': False, 'message': 'No OTP found for this phone number'}

        stored_data = otp_storage[phone]

        # Check if OTP has expired (5 minutes)
        if time.time() - stored_data['timestamp'] > 300:
            del otp_storage[phone]
            return {'success': False, 'message': 'OTP has expired'}

        # Check attempt limit
        if stored_data['attempts'] >= 3:
            del otp_storage[phone]
            return {'success': False, 'message': 'Maximum OTP attempts exceeded'}

        stored_data['attempts'] += 1

        if stored_data['otp'] == user_otp:
            del otp_storage[phone]  # Remove OTP after successful verification
            return {'success': True, 'message': 'OTP verified successfully'}
        else:
            return {'success': False, 'message': f'Invalid OTP. Attempts remaining: {3 - stored_data["attempts"]}'}


# def send_otp(phone_data):
#     return {"otp": 1234}