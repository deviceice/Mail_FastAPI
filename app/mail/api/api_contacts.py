from fastapi import APIRouter, Depends, Query
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from mail.database.db_session import get_session
from mail.database.crud_mail import *
from mail.utils_func_API import *
from mail.schemas.db.schemas_db import *
from mail.schemas.tags_api import tags_description_api

api_contacts = APIRouter(prefix="/api/v1/contacts")


@api_contacts.get('/objects',
                  tags=['Contacts'],
                  summary=tags_description_api['objects']['summary'],
                  description=tags_description_api['objects']['description']
                  )
@cache(expire=120, key_builder=lambda *args, **kwargs: "api_v1_objects")
async def get_objects(session: AsyncSession = Depends(get_session)):
    db_data = await get_abd_objects(session)
    result = []
    if db_data is None:
        return None
    for object_sid, parent_object_sid, name in db_data:
        result.append(ObjectOut(
            object_sid=object_sid,
            parent_object_sid=parent_object_sid,
            name=name
        ))
    return result


@api_contacts.get('/abonents',
                  tags=['Contacts'],
                  summary=tags_description_api['abonents']['summary'],
                  description=tags_description_api['abonents']['description'])
@cache(
    expire=120,
    key_builder=lambda func, *args, **kwargs: f"api_v1_abonents:{kwargs.get('kwargs', {}).get('object_sid', 'none')}"
)
async def get_contacts(object_sid: str = Query(None, description="sid объекта", example="1"),
                       session: AsyncSession = Depends(get_session)):
    db_data = await get_abd_abonents(session, object_sid)
    result = []
    if db_data is None:
        return None
    for abonent_sid, fio, address, object_sid, login, object_name, job_name in db_data:
        email = f"{address}@{object_sid}.{SettingsServer.DOMAIN_DEFAULT}" if address else None
        result.append(AbonentOut(
            abonent_sid=abonent_sid,
            fio=fio,
            address=address,
            object_sid=object_sid,
            login=login,
            email=email,
            object_name=object_name,
            job_name=job_name,
        ))
    return result
