# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# model/projects.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Project(BaseModel):
    _id: str
    project_key: str
    description: str
    created_at: str
    updated_at: str | None
    is_active: bool
    labels: list[str] = []
    model_config = {"extra": "forbid"}


class ProjectCreate(BaseModel):
    project_key: str
    description: str = ""
    is_active: bool = True
    labels: list[str] = []
    model_config = {"extra": "forbid"}


class ProjectUpdate(BaseModel):
    description: str = None
    is_active: bool = None
    labels: list[str] = []
    model_config = {"extra": "forbid"}
