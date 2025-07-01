from sqlalchemy import Column, Integer, String
import database
from database import Base # Add this import

class User(Base): # Now User can inherit from Base
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
