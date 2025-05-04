import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Временная таблица для разработки
class Users(Base):
    __tablename__ = "users"
    __table_args__ = ({"schema": "mail"})
    id = Column("id", Integer, primary_key=True, nullable=False)
    username = Column("username", sqlalchemy.String, nullable=False)
    domain = Column("domain", sqlalchemy.String, nullable=False)
    password_hash = Column("password_hash", sqlalchemy.String, nullable=False)
    home = Column("home", sqlalchemy.String, nullable=False)
    uid = Column("uid", Integer, nullable=False)
    gid = Column("gid", Integer, nullable=False)
    active = Column("active", Boolean, default=True)
