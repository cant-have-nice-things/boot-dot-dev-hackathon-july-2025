from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WeatherData(BaseModel):
    location: str
    temperature: float
    humidity: int
    pressure: Optional[float] = None
    timestamp: datetime
    source: str

class OracleSubmission(BaseModel):
    oracle_address: str
    weather_data: WeatherData
    reputation_score: Optional[float] = None