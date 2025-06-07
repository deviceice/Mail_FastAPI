import asyncio
import email

from fastapi import (APIRouter, HTTPException, Response, BackgroundTasks, Depends, Query, WebSocket,
                     WebSocketDisconnect)
from fastapi_cache.decorator import cache
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as status_code

from mail.imap_smtp_connect.imap_connection import get_imap_connection
from mail.imap_smtp_connect.smtp_connection import get_smtp_connection
from mail.database.db_session import get_session
from mail.database.crud_mail import *
from mail.settings_mail_servers.settings_server import SettingsServer
from mail.utils_func_API import *
from mail.schemas.request import *
from mail.schemas.response import *
from mail.schemas.db.schemas_db import *

from mail.schemas.tags_api import tags_description_api
from mail.example_schemas.response_schemas_examples import *
from mail.example_schemas.request_schemas_examples import *
from mail.options_emails import EmailFlags
from mail.http_exceptions.default_exception import HTTPExceptionMail

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
@cache(expire=120, key_builder=lambda *args, **kwargs: "api_v1_abonents")
async def get_contacts(object_sid: str = Query(None, description="sid объекта", example="1"),
                       session: AsyncSession = Depends(get_session)):
    db_data = await get_abd_abonents(session, object_sid)
    result = []
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
