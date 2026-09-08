from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from finlen_be.api.v1 import api_v1_router
from finlen_be.core.config import settings
from finlen_be.core.database import AsyncSessionLocal, engine
from finlen_be.core.firebase import initialize_firebase
from finlen_be.db.seed import seed_scenarios

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("finlen_be")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Firebase and ensure scenarios are seeded
    logger.info("Starting up %s in %s mode...", settings.APP_NAME, settings.APP_ENV)
    initialize_firebase()

    if settings.SEED_DB_ON_STARTUP:
        try:
            async with AsyncSessionLocal() as session:
                await seed_scenarios(session)
        except Exception as e:
            logger.error("Failed to run startup scenario check/seed: %s", e)

    yield

    # Shutdown: Dispose DB connection pool
    logger.info("Shutting down %s...", settings.APP_NAME)
    await engine.dispose()


app = FastAPI(
    title="FinLen API",
    description=(
        "Backend Core for **FinLen** — Interactive AI-Powered Financial Education Roleplay Platform.\n\n"
        "Provides user authentication, 10 predefined realistic financial scenarios, "
        "turn-by-turn AI decision evaluations with Google Gemini (gemini-2.5-flash), "
        "real-time stat changes, and Firebase Firestore synchronization."
    ),
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login, and JWT identity management",
        },
        {
            "name": "Scenarios",
            "description": "Browse and inspect predefined financial education scenarios",
        },
        {
            "name": "Roleplay",
            "description": "Interactive roleplay sessions, AI evaluations, stat tracking, and completion",
        },
    ],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes
app.include_router(api_v1_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs_url": "/docs",
        "version": "0.1.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}