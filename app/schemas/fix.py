from typing import Optional, List

from pydantic import BaseModel


class FixCreate(BaseModel):
    user_id: int
    problem: str
    solution: str

class FixUpdate(BaseModel):
    title: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    tags: Optional[List[str]] = None

class FixResponse(BaseModel):
    title: str
    problem: str
    solution: str
    tags: List[str]