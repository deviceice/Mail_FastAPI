import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Временная таблица для разработки
class Users(Base):
    __tablename__ = "users"
    __table_args__ = ({"schema": "mail"})
    id = Column("id", Integer, primary_key=True, nullable=True)
    login = Column("login", sqlalchemy.String, nullable=True)
    password = Column("password", sqlalchemy.String, nullable=True)
