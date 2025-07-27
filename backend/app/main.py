from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.spotify import router as spotify_router
#from .routes import playlist

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Nice Things - API",
    description="Activity Playlist Fuzzy Generator",
    version="1.0.0",
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "https://localhost:3001",
        "http://localhost:3001",
        "https://localhost:3001",
    ],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Nice Things API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(spotify_router, prefix="/api/v1")
#app.include_router(playlist.router, prefix="/api/v1")
