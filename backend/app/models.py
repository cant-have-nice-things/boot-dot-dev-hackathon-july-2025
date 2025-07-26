from datetime import datetime

from pydantic import BaseModel


class WeatherData(BaseModel):
    location: str
    temperature: float
    humidity: int
    pressure: float | None = None
    timestamp: datetime
    source: str


class OracleSubmission(BaseModel):
    oracle_address: str
    weather_data: WeatherData
    reputation_score: float | None = None
