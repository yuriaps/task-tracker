from fastapi import FastAPI

from app.api.routes import auth, tasks

app = FastAPI(title="Task Manager API", version="0.1.0")

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health", tags=["health"])
async def health_check():
    """Simple liveness check — useful for Docker healthchecks and load balancers."""
    return {"status": "ok"}
