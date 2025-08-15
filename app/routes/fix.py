from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.crud.fix import fix_crud
from app.db.session import get_db
from app.schemas.fix import FixResponse, FixCreate

import logging

router = APIRouter(
    tags=["fixes"],
)

logger = logging.getLogger(__name__)

@router.post("", response_model=FixResponse, status_code=status.HTTP_201_CREATED)
async def create_fix(fix: FixCreate, db: Session=Depends(get_db)):
    logger.info(f"Creating fix for the user with the id {fix.user_id}")
    created_fix = await fix_crud.create(db, fix)
    return created_fix

@router.get("", response_model=List[FixResponse], status_code=status.HTTP_200_OK)
async def get_all_fixes(db: Session=Depends(get_db)):
    return fix_crud.get_all(db=db)