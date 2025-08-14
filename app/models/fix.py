from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Fix(Base):
    __tablename__ = 'fixes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=True)
    problem = Column(String(255), nullable=False)
    solution = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now())
    # Foreign key to the users table
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

    # set the relationship with the users table
    user = relationship('User', back_populates='fixes')

    # set the relationship with the tags table
    tags = relationship('Tag', secondary='fix_tag', back_populates='fixes')