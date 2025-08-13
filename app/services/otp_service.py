import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.otp import OTP
from app.config import settings

def _generate_code(length=6):
    return "".join(str(random.randint(0,9)) for _ in range(length))

def create_otp(db: Session, phone: str):
    code = _generate_code(6)
    now = datetime.utcnow()
    expires = now + timedelta(seconds=settings.OTP_EXPIRY_SECONDS)
    otp = OTP(user_phone=phone, code=code, created_at=now, expires_at=expires, used=False)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp

def verify_otp(db: Session, phone: str, code: str):
    now = datetime.utcnow()
    q = db.query(OTP).filter(OTP.user_phone==phone, OTP.code==code, OTP.used==False, OTP.expires_at >= now)
    entry = q.order_by(OTP.created_at.desc()).first()
    if not entry:
        return False
    entry.used = True
    db.add(entry)
    db.commit()
    return True
