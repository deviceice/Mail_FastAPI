import asyncio
import email

from fastapi import (APIRouter, HTTPException, Response, BackgroundTasks, Depends, Query, WebSocket,
                     WebSocketDisconnect)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as status_code

from mail.imap_smtp_connect.imap_connection import get_imap_connection
from mail.imap_smtp_connect.smtp_connection import get_smtp_connection
from mail.database.db_session import get_session
from mail.database.crud_mail import *
from mail.utils_func_API import *
from mail.schemas.request.schemas_mail import *
from mail.schemas.response.schemas_mail import *
from mail.schemas.tags_api import tags_description_api
from mail.example_schemas.response_schemas_examples import *
from mail.example_schemas.request_schemas_examples import *
from mail.options_emails import EmailFlags
from mail.http_exceptions.default_exception import HTTPExceptionMail

api_contacts = APIRouter(prefix="/api/v1/contacts")


@api_contacts.get('/objects',
                  # response_model=GetMailsResponse,
                  # responses=get_mails_response_example,
                  tags=['Contacts'],
                  summary=tags_description_api['objects']['summary'],
                  description=tags_description_api['objects']['description']
                  )
async def get_objects(session: AsyncSession = Depends(get_session)):  # session: AsyncSession = Depends(get_session)
    db_data = await get_abd_objects(session)
    return db_data


@api_contacts.get('/abonents',
                  # response_model=GetMailsResponse,
                  # responses=get_mails_response_example,
                  tags=['Contacts'],
                  summary=tags_description_api['abonents']['summary'],
                  description=tags_description_api['abonents']['description']
                  )
async def get_objects(object_sid: str = Query(None, description="sid объекта", example="1"),
                      session: AsyncSession = Depends(get_session)):  # session: AsyncSession = Depends(get_session)
    db_data = await get_abd_abonents(session, object_sid)
    return db_data
