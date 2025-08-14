from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.models.fix_tag_junction import fix_tag_table
from app.db.base import Base

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    # set the relationship with the fix_tag table
    fixes = relationship('Fix', secondary='fix_tag', back_populates='tags')