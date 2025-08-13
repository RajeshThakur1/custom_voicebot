from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.otp_schema import SendOTPRequest, VerifyOTPRequest
from app.database import get_db
from app.services.otp_service import create_otp, verify_otp

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/send-otp")
def send_otp(payload: SendOTPRequest, db: Session = Depends(get_db)):
    otp = create_otp(db, payload.phone)
    return {"message": "OTP sent (dev mode)", "code": otp.code}

@router.post("/verify-otp")
def verify(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    ok = verify_otp(db, payload.phone, payload.code)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return {"message": "OTP verified"}
