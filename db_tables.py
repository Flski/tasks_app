from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db_config import DB


class User(DB):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    tasks = relationship("Task")

class Task(DB):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))