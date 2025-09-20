from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from datetime import datetime

#Models - Service History
class ServiceHistory(Base):
    __tablename__ = "service_history"
    service_id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicle_info.vehicle_id"))
    service_type = Column(String)
    date_service = Column(DateTime)
    odmeter_reading = Column(Float)
    warenty_status = Column(Boolean)
    cost_of_service = Column(Float)
    time_in = Column(DateTime)
    time_out = Column(DateTime)
    comments = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    edited_by = Column(String)
    vehicle = relationship("VehicleInfo", back_populates="services")

#Models - todos
class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Integer, default=1)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="todos")

#Models - users
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

#Models - Vehicle Info
class VehicleInfo(Base):
    __tablename__ = "vehicle_info"
    vehicle_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    registration_number = Column(String)
    chasie_number = Column(String)
    engineno = Column(String)
    yom = Column(String)  # Year of Manufacture
    make = Column(String)
    model = Column(String)
    date_of_sale = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    edited_by = Column(String)
    user = relationship("User", back_populates="vehicles")
    services = relationship("ServiceHistory", back_populates="vehicle")