from fastapi.responses import FileResponse

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from typing import Union, List
import traceback
import sys
import json
import shutil
from app.middlewares.auth_apikey import get_api_key
from app.services.otp_services import OTPService
from app.utilities.bia_logger import get_logger


logger = get_logger(__name__)

router = APIRouter(
    dependencies=[Depends(get_api_key)],
    responses={404: {"description": "Not found"}},
)

otp_services = OTPService()

@router.get("/", tags=["Health"])
async def health_check():
    """Check the health of services
    author: rajeshthakur@kronosx.ai
    Returns:
        [json]: json object with a status code 200 if everything is working fine else 400.
    """
    logger.debug("Health check requested")
    return {"message": "Status = Healthy"}


@router.post("/send-otp", tags=["Health"])
async def send_otp_end(phone_data):
    logger.info(f"Sending OTP to {phone_data}")
    otp = otp_services.generate_otp()
    return otp_services.send_otp(phone_data,otp)

    # return send_otp(phone_d


@router.post("/verify-otp",tags=["Health"])
async def verify_otp(phone_data,otp):
    logger.info(f"Verifying otp.....")
    return otp_services.verify_otp(phone_data,otp)


#     """Verify the entered OTP"""
#     try:
#         phone = verification_data.phone
#         user_otp = verification_data.otp
#
#         result = otp_service.verify_otp(phone, user_otp)
#
#         if result['success']:
#             return {
#                 "success": True,
#                 "message": result['message'],
#                 "phone": phone
#             }
#         else:
#             raise HTTPException(status_code=400, detail=result['message'])
#
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "OTP service is running"}
