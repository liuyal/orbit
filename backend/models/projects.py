# models/project.py

from pydantic import BaseModel


class Project(BaseModel):
    name: str
    short_name: str
    description: str
    id: str
    created_at: str
    updated_at: str
    test_cases: int
    test_cycles: int
    is_active: bool = True


class ProjectCreate(BaseModel):
    name: str
    short_name: str
    description: str
    id: str
