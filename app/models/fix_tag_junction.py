from sqlalchemy import Table, ForeignKey, Integer, Column

from app.db.base import Base

fix_tag_table = Table(
    'fix_tag',
    Base.metadata,
    Column('fix_id', Integer, ForeignKey('fixes.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)