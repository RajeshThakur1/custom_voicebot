from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    phonenumber = Column(String)
    name = Column(String)
    address = Column(String)
    email_id = Column(String, unique=True, index=True)
    id_varified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    edited_by = Column(String)
    vehicles = relationship("VehicleInfo", back_populates="user")