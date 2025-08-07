from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # set the relationship with the fixes table
    fixes = relationship('Fix', back_populates='user')