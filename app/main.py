from fastapi import FastAPI, Depends
from .database import engine, Base, get_db
from .models import Property, CrimeStat, MarketTrend # Imports from __init__.py

app = FastAPI(title="UrbanPulse 360 API")

# This triggers the table creation in Azure
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"status": "UrbanPulse modular structure is active"}