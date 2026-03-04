from fastapi import FastAPI
from .database import engine, Base
from .routers import market_router, investor_router

app = FastAPI(
    title="UrbanPulse 360 API",
    description="Property intelligence API for investors and relocators",
    version="0.1.0",
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(market_router)
app.include_router(investor_router)


@app.get("/", tags=["Health"])
def read_root():
    return {"status": "UrbanPulse 360 API is running", "version": "0.1.0"}