from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, voice

def create_app():
    app = FastAPI(title="Custom Voicebot")
    Base.metadata.create_all(bind=engine)
    app.include_router(auth.router)
    app.include_router(voice.router)
    return app

app = create_app()
