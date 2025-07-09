from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import Relationship
from database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    date = Column(String, index=True)
    complite = Column(Boolean)



