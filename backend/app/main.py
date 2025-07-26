from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import weather

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Weather Oracle API",
    description="Decentralized weather data oracle",
    version="1.0.0",
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Weather Oracle API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(weather.router, prefix="/api/v1")
