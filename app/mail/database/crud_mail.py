# Запросы в БД на этапе разработки
from mail.database.models_mail import *


# Test корректной работы сессии
async def db_test(session):
    async with session as s:
        check = await s.execute(
            select(Users))
        check = check.scalar()
        # print(check.id, check.login, check.password)
    return check
