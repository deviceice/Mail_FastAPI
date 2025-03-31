import asyncio

from fastapi import (APIRouter, Request, HTTPException, Response, BackgroundTasks, Depends, Query)
from starlette import status as status_code

from mail.imap_smtp_connect.imap_connection import get_imap_connection
from mail.imap_smtp_connect.smtp_connection import get_smtp_connection
from mail.support_func_API import *
from mail.schemas.request_schemas import *
from mail.schemas.response_schemas import *
from mail.schemas.tags_api import tags_description_api
from mail.example_schemas.response_schemas_examples import *
from mail.example_schemas.request_schemas_examples import *

import email

api_v1 = APIRouter(prefix="/api/v1")


@api_v1.get('/mails',
            response_model=GetMailsResponse,
            responses=get_mails_response_example,
            tags=['Get mails'],
            summary=tags_description_api['mails']['summary'],
            description=tags_description_api['mails']['description']
            )
async def emails(
        request: Request,
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        limit: Optional[int] = Query(20, description="Количество писем для получения (от 1 до 100)", ge=1, le=100),
        last_uid: Optional[str] = Query(None,
                                        description="Последний UID письма, после которого прислать следующие письма"),
        imap=Depends(get_imap_connection)):
    # settings: Settings = Depends(get_settings) Асинхронное использование Settings
    # test = ['user', 'user1', 'user2', 'user3', 'user4', 'user5', 'user6', 'user7', 'user8', 'user9', 'user10', 'user11',
    #             'user12']
    # user = random.choice(test)
    # print(settings.config['HOST_MAIL']['smtp_host'])
    status, response = await imap.list('""', '"*"')
    folders = await parse_folders(response) if status == 'OK' else None
    folder = await encode_name_utf7_ascii(mbox)
    try:
        status, response = await imap.select(folder)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    if status != 'OK':
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail="Папка не найдена в почтовом ящике")
    status_all, messages = await imap.uid_search("ALL")
    status_unread, messages_unseen = await imap.uid_search("UNSEEN")
    # print(status_unread, messages_unseen)
    # status_recent, messages_recent = await imap.uid_search("RECENT")
    # print(status_recent, messages_recent)
    # status, response = await imap.status(folder, '(MESSAGES UNSEEN RECENT)')
    # print(status, response)
    if status_all != 'OK' and status_unread != 'OK':
        await imap.close()
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    mails_uids = messages[0].decode().split()
    total_message = len(mails_uids)
    mails_uids_unseen = set(messages_unseen[0].decode().split())
    # mails_uids_recent = messages_recent[0].decode().split()
    # print(mails_uids, mails_uids_unseen, mails_uids_recent)
    mails_uids = await get_elements_inbox_uid(mails_uids, last_uid, limit if limit is not None else 20)
    status, msg_data_bytes = await imap.uid("FETCH", ",".join(mails_uids), "(FLAGS RFC822.HEADER BODYSTRUCTURE)")
    if status != 'OK':
        await imap.close()
        return {'status': True, 'total_message': 0, 'folders': folders, 'emails': []}

    msg_data, options_message = await clear_bytes_in_message(msg_data_bytes)
    emails = []
    for mail_uid, message, options in zip(mails_uids, msg_data, options_message):
        message = email.message_from_bytes(message)
        message_id = message.get("Message-ID", "").strip('<>')
        # print(mail_uid, options['uid'], options['attachments'])
        if message.get("References", ""):
            # print(message)
            continue
        main_message = {
            "uid": mail_uid,
            "message_id": message_id,
            "from": message["From"] if message["From"] else '',
            "to": message['To'].split(',') if message['To'] else '',
            "subject": await get_decode_header_subject(message),
            "date": message["Date"] if message["Date"] else '',
            "is_read": True if mail_uid not in mails_uids_unseen else False,
            "flags": options['flags'] if mail_uid == options['uid'] else False,
            "attachments": options['attachments'] if mail_uid == options['uid'] else [],
            "mails_referance": [],
        }
        if mbox == 'INBOX':
            search_criteria = f'HEADER References "{message_id}"'
            status_reference, references_data = await imap.uid_search(search_criteria)
            references_uids = references_data[0].decode().split() if status_reference == 'OK' else []
            status_message_reference, msg_data_reference_bytes = await imap.uid("FETCH", ",".join(references_uids),
                                                                                "(FLAGS RFC822.HEADER BODYSTRUCTURE)")

            msg_data_referances, options_references = await clear_bytes_in_message(msg_data_reference_bytes)
            # references_message = []
            for mail_uid_referance, msg_data_reference, option_reference in zip(references_uids, msg_data_referances,
                                                                                options_references):
                # print('msg_data_reference', msg_data_reference, option_reference)
                message_reference = email.message_from_bytes(msg_data_reference)
                # subject_reference = await get_decode_header_subject(message_reference)
                message_reference_id = message_reference.get("Message-ID", "").strip('<>')
                # mail_uid_referance.append(mail_uid_referance)
                referance_message = {
                    "uid": mail_uid_referance,
                    "message_id": message_reference_id,
                    "from": message_reference["From"] if message_reference["From"] else '',
                    "to": message_reference['To'].split(',') if message_reference['To'] else '',
                    "subject": await get_decode_header_subject(message_reference),
                    "date": message_reference["Date"] if message_reference["Date"] else '',
                    "is_read": True if mail_uid_referance not in mails_uids_unseen else False,
                    # "mails_referance": [],
                    "flags": option_reference['flags'] if mail_uid_referance == option_reference['uid'] else False,
                    "attachments": option_reference['attachments'] if mail_uid_referance == option_reference[
                        'uid'] else [],
                }
                # print(referance_message)
                main_message['mails_referance'].append(referance_message)
        emails.append(main_message)
    await imap.close()
    emails.reverse()
    return {'status': True, 'total_message': total_message, 'folders': folders, 'emails': emails}


@api_v1.post("/send_mail",
             openapi_extra=send_mail_request_example,
             tags=['Send mails'],
             summary=tags_description_api['send_mail']['summary'],
             description=tags_description_api['send_mail']['description']
             )
async def send_emails(email: EmailSend,
                      background_tasks: BackgroundTasks,
                      smtp=Depends(get_smtp_connection),
                      imap=Depends(get_imap_connection)):
    message = await create_email_with_attachments(email)
    try:
        await smtp.sendmail('user@mail.palas', email.to, message.as_string())
        return Response(status_code=status_code.HTTP_200_OK,
                        background=background_tasks.add_task(append_inbox_message_in_sent, message, imap))
    except Exception:
        raise HTTPException(status_code=status_code.HTTP_429_TOO_MANY_REQUESTS,
                            detail='Превышено колличество запросов к SMTP серверу')


@api_v1.get("/folders",
            responses=get_folders_response_example,
            tags=['Folders'],
            summary=tags_description_api['folders']['summary'],
            description=tags_description_api['folders']['description'])
async def folders(imap=Depends(get_imap_connection)):
    try:
        status, response = await imap.list('""', '"*"')
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    if status == 'OK':
        folders = await parse_folders(response)
        return {'status': True,
                'folders': folders}
    else:
        return {'status': False,
                'folders': None}


@api_v1.post("/create_folder",
             openapi_extra=create_folder_request_example,
             response_model=Default200Response,
             responses=create_folder_response_example,
             tags=['Folders'],
             summary=tags_description_api['create_folder']['summary'],
             description=tags_description_api['create_folder']['description']
             )
async def create_folder(mbox: NameFolder, imap=Depends(get_imap_connection)):
    name = await encode_name_utf7_ascii(mbox.name)
    try:
        status, response = await imap.create(name)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    if status == 'OK':
        return {'status': True,
                'message': f"Папка {mbox.name} успешно создана"}
    else:
        return {'status': False,
                'message': f"Не удалось создать папку {mbox.name}"}


@api_v1.post("/delete_folder",
             openapi_extra=delete_folder_request_example,
             response_model=Default200Response,
             responses=delete_folder_response_example,
             tags=['Folders'],
             summary=tags_description_api['delete_folder']['summary'],
             description=tags_description_api['delete_folder']['description']
             )
async def delete_folder(mbox: NameFolder, imap=Depends(get_imap_connection)):
    name = await encode_name_utf7_ascii(mbox.name)
    try:
        status, response = await imap.delete(name)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    if status == 'OK':
        return {'status': True,
                'message': f"Папка {mbox.name} успешно удалена"}
    else:
        return {'status': False,
                'message': f"Не удалось удалить папку {mbox.name}"}


@api_v1.post("/rename_folder",
             openapi_extra=rename_folder_request_example,
             response_model=Default200Response,
             responses=rename_folder_response_example,
             tags=['Folders'],
             summary=tags_description_api['rename_folder']['summary'],
             description=tags_description_api['rename_folder']['description']
             )
async def rename_folder(mbox: RenameFolder, imap=Depends(get_imap_connection)):
    old_name_folder = await encode_name_utf7_ascii(mbox.old_name_mbox)
    new_name_folder = await encode_name_utf7_ascii(mbox.new_name_mbox)
    try:
        status, response = await imap.rename(old_name_folder, new_name_folder)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    if status == 'OK':
        return {'status': True,
                'message': f"Папка {mbox.old_name_mbox} успешно переименована в {mbox.new_name_mbox}"}
    else:
        return {'status': False,
                'message': f"Не удалось переименовать папку {mbox.old_name_mbox}"}


@api_v1.get("/body_message",
            response_model=BodyResponse,
            responses=body_message_response_example,
            tags=['Body Mail'],
            summary=tags_description_api['body_message']['summary'],
            description=tags_description_api['body_message']['description'])
async def body_message(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        uid: str = Query(...,
                         description="UID письма", example="989"),
        imap=Depends(get_imap_connection)):
    folder = await encode_name_utf7_ascii(mbox)
    try:
        status, _ = await imap.select(folder)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    if status != 'OK':
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                            detail=f"Папка {mbox} не найдена в почтовом ящике")

    status, response = await imap.uid("FETCH", uid, "(BODY[HEADER] BODY[1.MIME] BODY[1] BODYSTRUCTURE)")
    await imap.close()
    if status != 'OK':
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    if len(response) == 1:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=f"Письмо не найдено с таким UID ={uid}")

    message_header = email.message_from_bytes(response[1])
    subject = await get_decode_header_subject(message_header)
    body_header = email.message_from_bytes(response[3])
    # print('body_header', body_header)
    # print(message)
    body = response[5].decode()
    # print('body_start', body)
    if body_header.get('Content-Transfer-Encoding') == 'base64':
        body = base64.b64decode(body)
        body = body.decode()
    # print('end', body)

    attachments = await get_name_attachments(response[6])

    return {'status': True,
            "uid": uid,
            "from": message_header["From"] if message_header["From"] else '',
            'to': message_header['To'].split(',') if message_header['To'] else [],
            "subject": subject if subject else '',
            "date": message_header["Date"] if message_header['Date'] else '',
            "body": body if body else '',
            'attachments': attachments}


@api_v1.get("/status_folder",
            response_model=StatusFolderResponse,
            responses=status_folder_response_example,
            tags=['Status folder'],
            summary=tags_description_api['status_folder']['summary'],
            description=tags_description_api['status_folder']['description'])
async def status_folder(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        imap=Depends(get_imap_connection)):
    status, response = await imap.status(mbox, '(MESSAGES UNSEEN RECENT)')
    if status == 'NO':
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail="Папка не найдена в почтовом ящике")

    if status != 'OK':
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    result = await parse_status_response(response[0])
    return result


# \\Flagged
@api_v1.get("/mark_read",
            response_model=StatusFlags,
            responses=status_flags_response_example,
            tags=['Flags'],
            summary=tags_description_api['mark_read']['summary'],
            description=tags_description_api['mark_read']['description'])
async def mark_read_unread(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        uid: str = Query(..., description="UID письма", example="989"),
        flag: bool = Query(..., description=""),
        imap=Depends(get_imap_connection)):
    folder = await encode_name_utf7_ascii(mbox)
    try:
        status, _ = await imap.select(folder)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    if status != 'OK':
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                            detail=f"Папка {mbox} не найдена в почтовом ящике")
    if flag:
        status, _ = await imap.uid("STORE", uid, "+FLAGS", "(\\Seen)")
        if status != 'OK':
            await imap.close()
            raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                                detail='Сервер IMAP не ответил')
    else:
        status, _ = await imap.uid("STORE", uid, "-FLAGS", "(\\Seen)")
        if status != 'OK':
            await imap.close()
            raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                                detail='Сервер IMAP не ответил')
    await imap.close()
    return {'status': True}


@api_v1.get("/mark_flagged",
            response_model=StatusFlags,
            responses=status_flags_response_example,
            tags=['Flags'],
            summary=tags_description_api['mark_flagged']['summary'],
            description=tags_description_api['mark_flagged']['description'])
async def mark_read_unread(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        uid: str = Query(..., description="UID письма", example="989"),
        flag: bool = Query(..., description=""),
        imap=Depends(get_imap_connection)):
    folder = await encode_name_utf7_ascii(mbox)
    try:
        status, _ = await imap.select(folder)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Сервер IMAP не ответил')
    if status != 'OK':
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                            detail=f"Папка {mbox} не найдена в почтовом ящике")
    if flag:
        status, _ = await imap.uid("STORE", uid, "+FLAGS", "(\\Flagged)")
        if status != 'OK':
            await imap.close()
            raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                                detail='Сервер IMAP не ответил')
    else:
        status, _ = await imap.uid("STORE", uid, "-FLAGS", "(\\Flagged)")
        if status != 'OK':
            await imap.close()
            raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                                detail='Сервер IMAP не ответил')
    await imap.close()
    return {'status': True}


@api_v1.post("/move_email",
             response_model=Default200Response,
             responses=move_emails_response_example,
             openapi_extra=move_mail_request_example,
             tags=['Move and Copy mails'],
             summary=tags_description_api['move_email']['summary'],
             description=tags_description_api['move_email']['description']
             )
async def move_email(
        move_emails: MoveEmails,
        imap=Depends(get_imap_connection)):
    # ",".join(mails_uids)
    try:
        encoded_source = await encode_name_utf7_ascii(move_emails.source_folder)
        encoded_target = await encode_name_utf7_ascii(move_emails.target_folder)
    except Exception as e:
        raise HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST,
                            detail=f"Ошибка кодирования имени папки: {str(e)}")
    try:
        status, _ = await imap.select(encoded_source)
        if status != 'OK':
            raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                                detail=f"Исходная папка '{move_emails.source_folder}' не найдена")

        # status, response = await imap.uid('COPY', uid, encoded_target)
        if isinstance(move_emails.uid, list):
            uid_str = ",".join(move_emails.uid)
        else:
            uid_str = move_emails.uid
        status, response = await imap.uid('MOVE', uid_str, encoded_target)
        if status != 'OK':
            raise HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST,
                                detail=f"Не удалось переместить письмо:")
        return {
            "status": True,
            "message": f"Письмо(а) {move_emails.uid} успешно перемещены из '{move_emails.source_folder}' в '{move_emails.target_folder}'",
        }

    except asyncio.exceptions.TimeoutError:
        raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Таймаут соединения с IMAP-сервером')
    finally:
        try:
            await imap.close()
        except Exception as e:
            raise HTTPException(status_code=status_code.HTTP_503_SERVICE_UNAVAILABLE,
                                detail=f"Ошибка в Backend: {str(e)}")




# @api_v1.get("/move_email",
#             description="Перемещает письмо из текущей папки в указанную целевую папку")
# async def move_email(
#         source_folder: str = Query(..., description="Исходная папка, где находится письмо", example="INBOX"),
#         target_folder: str = Query(..., description="Целевая папка для перемещения", example="АРХИВ"),
#         uid: str = Query(..., description="UID письма для перемещения", example="989"),
#         imap=Depends(get_imap_connection)):
#     try:
#         encoded_source = await encode_name_utf7_ascii(source_folder)
#         encoded_target = await encode_name_utf7_ascii(target_folder)
#     except Exception as e:
#         raise HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST,
#                             detail=f"Ошибка кодирования имени папки: {str(e)}")
#     try:
#         status, _ = await imap.select(encoded_source)
#         if status != 'OK':
#             raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
#                                 detail=f"Исходная папка '{source_folder}' не найдена")
#
#         status, response = await imap.uid('COPY', uid, encoded_target)
#         print(status, response)
#         if status != 'OK':
#             raise HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST,
#                                 detail=f"Не удалось скопировать письмо:")
#
#         status, response = await imap.uid('STORE', uid, '+FLAGS', '(\\Deleted)')
#         print(status, response)
#         if status != 'OK':
#             raise HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST,
#                                 detail=f"Не удалось пометить письмо для удаления:")
#
#         status, response = await imap.expunge()
#         if status != 'OK':
#             raise HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST,
#                                 detail=f"Не удалось удалить письмо")
#         return {
#             "status": True,
#             "message": f"Письмо {uid} успешно перемещено из '{source_folder}' в '{target_folder}'",
#             "uid": uid
#         }
#
#     except asyncio.exceptions.TimeoutError:
#         raise HTTPException(status_code=status_code.HTTP_504_GATEWAY_TIMEOUT,
#                             detail='Таймаут соединения с IMAP-сервером')
#     except Exception as e:
#         raise HTTPException(status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
#                             detail=f"Ошибка при перемещении письма: {str(e)}")
#     finally:
#         try:
#             await imap.close()
#         except Exception as e:
#             raise HTTPException(status_code=status_code.HTTP_503_SERVICE_UNAVAILABLE,
#                                 detail=f"Ошибка в Backend: {str(e)}")
