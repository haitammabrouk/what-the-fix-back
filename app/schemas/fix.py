from typing import Optional, List
from pydantic.v1 import BaseModel

class FixCreate(BaseModel):
    problem: Optional[str] = None
    solution: Optional[str] = None

class FixUpdate(BaseModel):
    title: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    tags: Optional[List[str]] = None