# Запросы в БД на этапе разработки
from mail.database.models_mail import *


# Test корректной работы сессии
async def get_abd_objects(session):
    async with session as s:
        db_data = await s.execute(
            select(AbdObject))
        db_data = db_data.scalars().all()
        # print(db_data)
        return db_data


async def get_abd_abonents(session, object_sid):
    async with session as s:
        if object_sid is not None:
            db_data = await s.execute(
                select(AbdAbonent).where(AbdAbonent.object_sid == object_sid))
        else:
            db_data = await s.execute(
                select(AbdAbonent))
        db_data = db_data.scalars().all()
        # print(db_data)
        return db_data
