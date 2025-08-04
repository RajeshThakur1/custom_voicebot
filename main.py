from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User, VehicleInfo, ServiceHistory
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Customer Support Voice Bot API",
    description="FastAPI application for managing customer vehicle service data",
    version="1.0.0"
)

# Pydantic models for API requests/responses
class UserBase(BaseModel):
    phonenumber: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    email_id: Optional[EmailStr] = None
    id_varified: bool = False

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class VehicleInfoBase(BaseModel):
    registration_number: Optional[str] = None
    chasie_number: Optional[str] = None
    engineno: Optional[str] = None
    yom: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    date_of_sale: Optional[datetime] = None

class VehicleInfoCreate(VehicleInfoBase):
    user_id: int

class VehicleInfoResponse(VehicleInfoBase):
    vehicle_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ServiceHistoryBase(BaseModel):
    service_type: Optional[str] = None
    date_service: Optional[datetime] = None
    odmeter_reading: Optional[float] = None
    warenty_status: Optional[bool] = None
    cost_of_service: Optional[float] = None
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    comments: Optional[str] = None

class ServiceHistoryCreate(ServiceHistoryBase):
    vehicle_id: int

class ServiceHistoryResponse(ServiceHistoryBase):
    service_id: int
    vehicle_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Customer Support Voice Bot API is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# User endpoints
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@app.get("/users/email/{email_id}", response_model=UserResponse)
async def get_user_by_email(email_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email_id == email_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Vehicle endpoints
@app.post("/vehicles/", response_model=VehicleInfoResponse)
async def create_vehicle(vehicle: VehicleInfoCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.user_id == vehicle.user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_vehicle = VehicleInfo(**vehicle.dict())
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle

@app.get("/vehicles/{vehicle_id}", response_model=VehicleInfoResponse)
async def get_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VehicleInfo).where(VehicleInfo.vehicle_id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@app.get("/users/{user_id}/vehicles/", response_model=List[VehicleInfoResponse])
async def get_user_vehicles(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VehicleInfo).where(VehicleInfo.user_id == user_id))
    vehicles = result.scalars().all()
    return vehicles

# Service History endpoints
@app.post("/service-history/", response_model=ServiceHistoryResponse)
async def create_service_history(service: ServiceHistoryCreate, db: AsyncSession = Depends(get_db)):
    # Check if vehicle exists
    result = await db.execute(select(VehicleInfo).where(VehicleInfo.vehicle_id == service.vehicle_id))
    vehicle = result.scalar_one_or_none()
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db_service = ServiceHistory(**service.dict())
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service

@app.get("/service-history/{service_id}", response_model=ServiceHistoryResponse)
async def get_service_history(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ServiceHistory).where(ServiceHistory.service_id == service_id))
    service = result.scalar_one_or_none()
    if service is None:
        raise HTTPException(status_code=404, detail="Service history not found")
    return service

@app.get("/vehicles/{vehicle_id}/service-history/", response_model=List[ServiceHistoryResponse])
async def get_vehicle_service_history(vehicle_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ServiceHistory).where(ServiceHistory.vehicle_id == vehicle_id))
    services = result.scalars().all()
    return services

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)