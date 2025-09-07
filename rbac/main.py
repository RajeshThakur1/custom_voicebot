from fastapi import FastAPI
from models import User, Todos, VehicleInfo, ServiceHistory
from database import engine, SessionLocal
from routers import auth, todos, admin, users

app = FastAPI()

from models import User, Todos, VehicleInfo, ServiceHistory
from database import Base
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(admin.router)

# root
@app.get("/")

def root():
    return {"message": "RBAC FastAPI is running"}

#for DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



        
