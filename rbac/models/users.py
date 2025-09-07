from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phonenumber = Column(String)
    name = Column(String)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    address = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    id_varified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    edited_by = Column(String)

    todos = relationship("Todos", back_populates="owner", cascade="all, delete-orphan")
    vehicles = relationship("VehicleInfo", back_populates="user")