from fastapi import APIRouter, HTTPException
from app.models import WeatherData, OracleSubmission
from typing import List

router = APIRouter(prefix="/weather", tags=["weather"])

# Temporary in-memory storage (replace with database later)
weather_submissions: List[OracleSubmission] = []

@router.post("/submit")
async def submit_weather_data(submission: OracleSubmission):
    """Submit weather data from oracle"""
    weather_submissions.append(submission)
    return {"message": "Weather data submitted", "id": len(weather_submissions)}

@router.get("/latest/{location}")
async def get_latest_weather(location: str):
    """Get latest weather data for location"""
    location_data = [s for s in weather_submissions if s.weather_data.location.lower() == location.lower()]
    if not location_data:
        raise HTTPException(status_code=404, detail="No data found for location")

    # Return most recent
    latest = max(location_data, key=lambda x: x.weather_data.timestamp)
    return latest

@router.get("/submissions")
async def get_all_submissions():
    """Get all weather submissions"""
    return weather_submissions