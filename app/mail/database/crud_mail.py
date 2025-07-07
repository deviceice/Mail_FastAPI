from mail.database.models_mail import *


# Запросы в БД на этапе разработки
async def get_abd_objects(session):
    query = select(AbdObject.object_sid,
                   AbdObject.parent_object_sid,
                   AbdObject.name,
                   )
    async with session as s:
        result = await s.execute(query)
    return result.fetchall()


async def get_abd_abonents(session, object_sid):
    query = select(
        AbdAbonent.abonent_sid,
        AbdAbonent.fio,
        AbdAbonent.address,
        AbdAbonent.object_sid,
        AbdAbonent.login,
        AbdObject.name.label("object_name"),
        AbdAbonent.job_name,
    ).join(
        AbdObject, AbdAbonent.object_sid == AbdObject.object_sid
    )

    if object_sid:
        query = query.where(AbdAbonent.object_sid == object_sid)
    async with session as s:
        result = await s.execute(query)
    return result.fetchall()
