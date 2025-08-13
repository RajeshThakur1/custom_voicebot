from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from app.database import Base

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    user_phone = Column(String(50), index=True, nullable=False)
    code = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
