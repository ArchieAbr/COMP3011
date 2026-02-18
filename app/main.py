from fastapi import FastAPI

app = FastAPI(title="UrbanPulse API")

@app.get("/")
def read_root():
    return {"status": "UrbanPulse is Online"}