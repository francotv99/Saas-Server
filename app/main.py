from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import auth, tasks, organizations
from app.core.redis import close_redis

app = FastAPI(
    title="TaskFlow SaaS API",
    description="Multi-tenant SaaS backend API with FastAPI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_PREFIX}/tasks", tags=["tasks"])
app.include_router(organizations.router, prefix=f"{settings.API_V1_PREFIX}/organizations", tags=["organizations"])


@app.get("/")
async def root():
    return {
        "message": "TaskFlow SaaS API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()
