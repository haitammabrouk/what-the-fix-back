from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.crud.fix import fix_crud
from app.db.session import get_db
from app.schemas.fix import FixResponse, FixCreate

router = APIRouter(
    tags=["fixes"],
)

@router.post("", response_model=FixResponse, status_code=status.HTTP_201_CREATED)
async def create_fix(fix: FixCreate, db: Session=Depends(get_db)):
    return fix_crud.create(db=db, fix=fix)

@router.get("", response_model=List[FixResponse], status_code=status.HTTP_200_OK)
async def get_all_fixes(db: Session=Depends(get_db)):
    return fix_crud.get_all(db=db)