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
        query = select(
            AbdAbonent,
            AbdObject.name.label("object_name")
        ).join(
            AbdObject,
            AbdAbonent.object_sid == AbdObject.object_sid
        )

        # Добавляем условие фильтрации, если указан object_sid
        if object_sid is not None:
            query = query.where(AbdAbonent.object_sid == object_sid)

        # Выполняем запрос
        result = await s.execute(query)
        db_data = result.all()

        return db_data
