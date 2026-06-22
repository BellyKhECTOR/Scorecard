"""FastAPI dependencies."""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.config import Settings, get_settings
from src.database import get_db


def get_settings_dep() -> Settings:
    return get_settings()


def get_session(db: Session = Depends(get_db)) -> Session:
    return db
