from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.predict import router
from app.database.db import Base, engine
from app.database import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NeuroBiomeX"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def home():
    return {
        "message": "Backend running successfully"
    }