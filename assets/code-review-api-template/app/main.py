from fastapi import FastAPI

from app.api.routes import router
from app.db.database import Base, engine


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    app = FastAPI(title="AI Code Review & Test Case Generator")
    app.include_router(router)
    return app


app = create_app()
