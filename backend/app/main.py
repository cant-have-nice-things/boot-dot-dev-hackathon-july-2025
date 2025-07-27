import logging
from os import getenv
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dependencies import (
    get_reccobeats_client,
    get_reccobeats_config,
    get_redis_client,
    get_redis_config,
    get_spotify_client,
    get_spotify_config,
)
from .routes.playlist import router as playlist_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting up application...")

    # Initialize Redis connection
    try:
        redis_config = get_redis_config()
        redis_client = get_redis_client(redis_config)
        await redis_client.connect()
        logger.info("Redis connection established")
        app.state.redis_client = redis_client
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        app.state.redis_client = None

    # Initialize Spotify connection
    try:
        spotify_config = get_spotify_config()
        spotify_client = get_spotify_client(spotify_config)
        connected = await spotify_client.connect()
        if connected:
            logger.info("Spotify connection established")
        else:
            logger.warning("Spotify connection failed - check authentication")
        app.state.spotify_client = spotify_client
    except Exception as e:
        logger.error(f"Failed to initialize Spotify: {e}")
        app.state.spotify_client = None

    # Initialize ReccoBeats connection (test connectivity)
    try:
        reccobeats_config = get_reccobeats_config()
        reccobeats_client = get_reccobeats_client(reccobeats_config)
        # Test with a simple metadata fetch (we don't need the result, just testing connectivity)
        _ = reccobeats_client.fetch_metadata_batch(["test_id"])
        logger.info("ReccoBeats connection tested successfully")
        app.state.reccobeats_client = reccobeats_client
    except Exception as e:
        logger.error(f"Failed to initialize ReccoBeats: {e}")
        app.state.reccobeats_client = None

    yield

    # Cleanup
    logger.info("Shutting down application...")
    if hasattr(app.state, "redis_client") and app.state.redis_client:
        await app.state.redis_client.disconnect()
        logger.info("Redis connection closed")


app = FastAPI(
    title="Nice Things - API",
    description="Activity Playlist Generator",
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins = getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Nice Things API"}


@app.get("/health")
async def health_check():
    """Health check endpoint that includes service status."""
    redis_status = False
    spotify_status = False
    reccobeats_status = False

    try:
        if hasattr(app.state, "redis_client") and app.state.redis_client:
            redis_status = await app.state.redis_client.ping()
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")

    try:
        if hasattr(app.state, "spotify_client") and app.state.spotify_client:
            spotify_status = app.state.spotify_client.is_connected()
    except Exception as e:
        logger.warning(f"Spotify health check failed: {e}")

    try:
        if hasattr(app.state, "reccobeats_client") and app.state.reccobeats_client:
            # Simple test - if client exists, consider it healthy
            reccobeats_status = True
    except Exception as e:
        logger.warning(f"ReccoBeats health check failed: {e}")

    return {
        "status": "healthy",
        "redis_connected": redis_status,
        "spotify_connected": spotify_status,
        "reccobeats_available": reccobeats_status,
    }


# Include routers
app.include_router(playlist_router, prefix="/api/v1")
