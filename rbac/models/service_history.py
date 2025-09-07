from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


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