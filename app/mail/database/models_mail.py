import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP

Base = declarative_base()


# Временная таблица для разработки
# class Users(Base):
#     __tablename__ = "users"
#     __table_args__ = ({"schema": "mail"})
#     id = Column("id", Integer, primary_key=True, nullable=False)
#     username = Column("username", sqlalchemy.String, nullable=False)
#     domain = Column("domain", sqlalchemy.String, nullable=False)
#     password_hash = Column("password_hash", sqlalchemy.String, nullable=False)
#     home = Column("home", sqlalchemy.String, nullable=False)
#     uid = Column("uid", Integer, nullable=False)
#     gid = Column("gid", Integer, nullable=False)
#     active = Column("active", Boolean, default=True)
class AbdObject(Base):
    __tablename__ = 'abd_object'
    __table_args__ = {'schema': 'ospo'}  # Указываем схему ospo

    object_sid = Column("object_sid", Integer, Sequence('abd_object_seq', schema='ospo'),
                        primary_key=True,
                        nullable=False,
                        server_default=text("nextval(('ospo.abd_object_seq'::text)::regclass)"),
                        comment='СИД Объекта'
                        )
    parent_object_sid = Column("parent_object_sid", Integer, comment='ССылка на СИД старшего объекта')
    address = Column("address", Integer, nullable=False, comment='Уникальный адрес объекта')
    level_code = Column("level_code", String(20), comment='код уровня объекта (public.classificator_body)')
    bcs_obj_sid = Column("bcs_obj_sid", Integer, comment='Ссылка на реальный объект в БЧС')
    name = Column("name", String(100), comment='Наименование')
    our = Column("our", Integer, comment='Признак своего(1)')
    work_mode_sid = Column("work_mode_sid", Integer)
    war_level_sid = Column("war_level_sid", Integer)
    lock = Column("lock", Integer, default=0, comment='Заблокирован объект(1) или нет(0)')
    oper_time_from = Column("oper_time_from", PG_TIMESTAMP(precision=0, timezone=False),
                            comment='Время начала операции (без часового пояса)')
    object_code = Column("object_code", String(50))
    obj_login = Column("obj_login", String(1))


class AbdAbonent(Base):
    __tablename__ = 'abd_abonent'
    __table_args__ = {'schema': 'ospo'}
    abonent_sid = Column("abonent_sid", Integer,
                         Sequence('abd_abonent_seq', schema='ospo'),
                         primary_key=True,
                         server_default=text("nextval(('ospo.abd_abonent_seq'::text)::regclass)"),
                         comment='СИД абонента'
                         )
    object_sid = Column("object_sid", Integer, nullable=False, comment='СИД объекта *')
    arm_sid = Column("arm_sid", Integer, comment='СИД АРМа абонента')
    fio = Column("fio", String(50))
    group_sid = Column("group_sid", Integer, comment='*')
    npp = Column("npp", Integer, comment='Номер по порядку')
    email = Column("email", String(100))
    security_level = Column("security_level", Integer, comment='Текущий уровень секретности абонента')
    address = Column("address", Integer, comment='Уникальный адрес абонента внутри объекта')
    login = Column("login", String(20))
    bcs_job_sid = Column("bcs_job_sid", Integer, comment='СИД должности из БЧС')
    rank_code = Column("rank_code", String(20), comment='код(!) звания абонента')
    lock = Column("lock", Integer, default=0, comment='Признак заблокирован(1) абонент или нет(0)')
    abonent_code = Column("abonent_code", String(50))
    job_name = Column("job_name", String)
    job_code = Column("job_code", String)
