from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class VehicleInfo(Base):
    __tablename__ = "vehicle_info"
    vehicle_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
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