from typing import List

from sqlalchemy.orm import Session

from app.schemas.fix import FixCreate
from app.models.fix import Fix


class FixCrud:
    def create(self, db: Session, fix: FixCreate) -> Fix:
        fix = Fix(**fix.dict())
        db.add(fix)
        db.commit()
        db.refresh(fix)
        return fix

    def get_all(self, db: Session) -> List[Fix]:
        fixes = db.query(Fix).all()
        return fixes

fix_crud = FixCrud()