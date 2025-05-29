import asyncio
import urllib.parse

from fastapi import (APIRouter, HTTPException, Response, BackgroundTasks, Depends, Query)
from fastapi.responses import StreamingResponse
from starlette import status as status_code

from mail.example_schemas.request_schemas_examples import *
from mail.example_schemas.response_schemas_examples import *
from mail.http_exceptions.default_exception import HTTPExceptionMail
from mail.imap_smtp_connect.imap_connection import get_imap_connection
from mail.imap_smtp_connect.smtp_connection import get_smtp_connection
from mail.options_emails import EmailFlags
from mail.schemas.request.schemas_mail import *
from mail.schemas.response.schemas_mail import *
from mail.schemas.tags_api import tags_description_api
from mail.utils_func_API import *

api_v1 = APIRouter(prefix="/api/v1")


@api_v1.get('/mails',
            response_model=GetMailsResponse,
            responses=get_mails_response_example,
            tags=['Get mails'],
            summary=tags_description_api['mails']['summary'],
            description=tags_description_api['mails']['description']
            )
async def emails(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        limit: Optional[int] = Query(20, description="Количество писем для получения (от 1 до 100)",
                                     ge=1, le=10000),
        last_uid: Optional[str] = Query(None,
                                        description="Последний UID письма, после которого прислать следующие письма"),
        imap=Depends(get_imap_connection)):
    try:
        status, response = await imap.list('""', '"*"')
        if status != 'OK':
            raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
        all_folders: Optional[list[str]] = await parse_folders(response) if status == 'OK' else None
        folder = await encode_name_utf7_ascii(name=mbox)
        status, response = await imap.select(folder)
        if status != 'OK':
            raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504

    status_all, messages = await imap.uid_search("ALL")
    status_unread, messages_unseen = await imap.uid_search("UNSEEN")
    if status_all != 'OK' and status_unread != 'OK':
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    mails_uids, mails_uids_unseen, total_message = await get_mails_uids_unseen(messages=messages,
                                                                               messages_unseen=messages_unseen)
    mails_uids = await get_elements_inbox_uid(arr=mails_uids, last_uid=last_uid,
                                              limit=limit if limit is not None else 20)
    if not mails_uids:
        return {'status': False, 'total_message': total_message, 'folders': all_folders, 'emails': []}
    status, msg_data_bytes = await imap.uid("FETCH", ",".join(mails_uids), "(FLAGS RFC822.HEADER BODYSTRUCTURE)")
    if status != 'OK':
        return {'status': False, 'total_message': total_message, 'folders': all_folders, 'emails': []}
    emails_list = []
    msg_data, options_message = await clear_bytes_in_message(message=msg_data_bytes)

    for mail_uid, message, options in zip(mails_uids, msg_data, options_message):
        message = email.message_from_bytes(message)

        main_message = await get_message_struct(mail_uid=mail_uid, mails_uids_unseen=mails_uids_unseen,
                                                message=message, options=options)
        emails_list.append(main_message)
    emails_list.reverse()
    # emails_list = await sort_emails(emails_list)
    return {'status': True, 'total_message': total_message, 'folders': all_folders, 'emails': emails_list}


@api_v1.get('/mail',
            response_model=GetMailResponse,
            responses=get_mail_response_example,
            tags=['Get mails'],
            summary=tags_description_api['mail']['summary'],
            description=tags_description_api['mail']['description']
            )
async def emails(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        number: Optional[str] = Query(...,
                                      description="Порядковый номер письма, которое прислать"),
        imap=Depends(get_imap_connection)):
    try:
        folder = await encode_name_utf7_ascii(name=mbox)
        status, response = await imap.select(folder)
        if status != 'OK':
            raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    status, msg_data_bytes = await imap.fetch(number, "(UID FLAGS BODY.PEEK[HEADER] BODYSTRUCTURE)")
    if status != 'OK':
        return {'status': False, 'mail': None}
    message_msg, options, uid = await clear_bytes_in_message_for_number(message=msg_data_bytes)
    message = email.message_from_bytes(message_msg[0])
    main_message = await get_message_struct(mail_uid=uid, mails_uids_unseen=None,
                                            message=message, options=options[0])
    return {'status': True, 'mail': main_message}


# @api_v1.get('/mails',
#             response_model=GetMailsResponse,
#             responses=get_mails_response_example,
#             tags=['Get mails'],
#             summary=tags_description_api['mails']['summary'],
#             description=tags_description_api['mails']['description']
#             )
# async def emails(
#         mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
#         limit: Optional[int] = Query(20, description="Количество писем для получения (от 1 до 100)",
#                                      ge=1, le=500),
#         last_uid: Optional[str] = Query(None,
#                                         description="Последний UID письма, после которого прислать следующие письма"),
#         imap=Depends(get_imap_connection)):  # session: AsyncSession = Depends(get_session)
#
#     try:
#         status, response = await imap.list('""', '"*"')
#         if status != 'OK':
#             raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
#         all_folders: Optional[list[str]] = await parse_folders(response) if status == 'OK' else None
#         folder = await encode_name_utf7_ascii(name=mbox)
#         status, response = await imap.select(folder)
#         if status != 'OK':
#             raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
#     except asyncio.exceptions.TimeoutError:
#         raise HTTPExceptionMail.IMAP_TIMEOUT_504
#
#     status_all, messages = await imap.uid_search("ALL")
#     status_unread, messages_unseen = await imap.uid_search("UNSEEN")
#     # status_recent, messages_recent = await imap.uid_search("RECENT")
#     # status, response = await imap.status(folder, '(MESSAGES UNSEEN RECENT)')
#     if status_all != 'OK' and status_unread != 'OK':
#         raise HTTPExceptionMail.IMAP_TIMEOUT_504
#     mails_uids, mails_uids_unseen, total_message = await get_mails_uids_unseen(messages=messages,
#                                                                                messages_unseen=messages_unseen)
#     mails_uids = await get_elements_inbox_uid(arr=mails_uids, last_uid=last_uid,
#                                               limit=limit if limit is not None else 20)
#     if not mails_uids:
#         return {'status': False, 'total_message': total_message, 'folders': all_folders, 'emails': []}
#     status, msg_data_bytes = await imap.uid("FETCH", ",".join(mails_uids), "(FLAGS RFC822.HEADER BODYSTRUCTURE)")
#     if status != 'OK':
#         return {'status': False, 'total_message': total_message, 'folders': all_folders, 'emails': []}
#
#     emails_list = []
#     msg_data, options_message = await clear_bytes_in_message(message=msg_data_bytes)
#     # id_message_main_reference = set()
#     for mail_uid, message, options in zip(mails_uids, msg_data, options_message):
#         message = email.message_from_bytes(message)
#         if message.get("References", ""):
#             # id_message_main_reference.add(re.findall(r'<([^>]+)>', message.get('References', ""))[0])
#             continue
#         main_message = await get_message_struct(mail_uid=mail_uid, mails_uids_unseen=mails_uids_unseen,
#                                                 message=message, options=options)
#
#         # Это временное условия для forntend, все вынесется в функцию и изменится получение для сокращения ответа API
#         if mbox == 'INBOX':
#             message_id = message.get("Message-ID", "").strip('<>')
#             search_criteria = f'HEADER References "{message_id}"'
#             status_reference, references_data = await imap.uid_search(search_criteria)
#             references_uids = references_data[0].decode().split() if status_reference == 'OK' else []
#             if len(references_uids) == 0:
#                 pass
#             else:
#                 status_message_reference, msg_data_reference_bytes = await imap.uid("FETCH", ",".join(references_uids),
#                                                                                     "(FLAGS RFC822.HEADER BODYSTRUCTURE)")
#                 msg_data_references, options_references = await clear_bytes_in_message(msg_data_reference_bytes)
#                 for mail_uid_reference, msg_data_reference, option_reference in zip(references_uids,
#                                                                                     msg_data_references,
#                                                                                     options_references):
#                     message_reference = email.message_from_bytes(msg_data_reference)
#                     reference_message = await get_message_ref_struct(mail_uid_reference=mail_uid_reference,
#                                                                      mails_uids_unseen=mails_uids_unseen,
#                                                                      message_reference=message_reference,
#                                                                      option_reference=option_reference)
#                     main_message['uid_last_ref'] = mail_uid_reference
#                     main_message['mails_reference'].append(reference_message)
#         emails_list.append(main_message)
#
#     emails_list.reverse()
#     emails_list = await sort_emails(emails_list)
#
#     return {'status': True, 'total_message': total_message, 'folders': all_folders, 'emails': emails_list}


@api_v1.get('/new_mails',
            response_model=GetNewMailsResponse,
            responses=get_mails_response_example,
            tags=['Get mails'],
            summary=tags_description_api['new_mails']['summary'],
            description=tags_description_api['new_mails']['description']
            )
async def new_mails(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        imap=Depends(get_imap_connection)):
    folder = await encode_name_utf7_ascii(name=mbox)
    try:
        status, response = await imap.select(folder)
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
    status_recent, messages_recent = await imap.uid_search("RECENT")
    if status_recent != 'OK':
        raise HTTPExceptionMail.IMAP_TIMEOUT_504

    mails_uids_recents, total_message_recent = await get_mails_uids_recent(messages_recent=messages_recent)
    status, msg_data_bytes = await imap.uid("FETCH", ",".join(mails_uids_recents),
                                            "(FLAGS RFC822.HEADER BODYSTRUCTURE)")
    if status != 'OK':
        return {'status': False, 'total_message': total_message_recent, 'emails': []}
    emails_list = []
    msg_data, options_messages = await clear_bytes_in_message(message=msg_data_bytes)

    for mail_uid, message, options in zip(mails_uids_recents, msg_data, options_messages):
        message = email.message_from_bytes(message)
        # message_id = message.get("Message-ID", "").strip('<>')
        main_message = await get_new_message_struct(mail_uid=mail_uid, message=message, options=options)
        emails_list.append(main_message)

    emails_list.reverse()
    return {'status': True, 'total_message': total_message_recent, 'emails': emails_list}


@api_v1.post("/send_mail",
             openapi_extra=send_mail_request_example,
             tags=['Send mails'],
             summary=tags_description_api['send_mail']['summary'],
             description=tags_description_api['send_mail']['description']
             )
async def send_emails(email_send: EmailSend,
                      background_tasks: BackgroundTasks,
                      smtp=Depends(get_smtp_connection),
                      imap=Depends(get_imap_connection)):
    message = await create_email_with_attachments(email_send)
    try:
        await smtp.sendmail('user@mail.palas', email_send.to, message.as_string())
        return Response(status_code=status_code.HTTP_200_OK,
                        background=background_tasks.add_task(append_inbox_message_in_sent, message, imap))
    except Exception:
        raise HTTPExceptionMail.SMTP_TOO_MANY_REQUESTS_429


@api_v1.get("/folders",
            responses=get_folders_response_example,
            tags=['Folders'],
            summary=tags_description_api['folders']['summary'],
            description=tags_description_api['folders']['description'])
async def folders(imap=Depends(get_imap_connection)):
    try:
        status, response = await imap.list('""', '"*"')
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status == 'OK':
        folders = await parse_folders(response)
        return {'status': True, 'folders': folders}
    else:
        return {'status': False, 'folders': None}


@api_v1.post("/create_folder",
             openapi_extra=create_folder_request_example,
             response_model=Default200Response,
             responses=create_folder_response_example,
             tags=['Folders'],
             summary=tags_description_api['create_folder']['summary'],
             description=tags_description_api['create_folder']['description']
             )
async def create_folder(mbox: NameFolder, imap=Depends(get_imap_connection)):
    name = await encode_name_utf7_ascii(name=mbox.name)
    try:
        status, response = await imap.create(name)
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status == 'OK':
        return {'status': True, 'message': f"Папка {mbox.name} успешно создана"}
    else:
        return {'status': False, 'message': f"Не удалось создать папку {mbox.name}"}


@api_v1.post("/delete_folder",
             openapi_extra=delete_folder_request_example,
             response_model=Default200Response,
             responses=delete_folder_response_example,
             tags=['Folders'],
             summary=tags_description_api['delete_folder']['summary'],
             description=tags_description_api['delete_folder']['description']
             )
async def delete_folder(mbox: NameFolder, imap=Depends(get_imap_connection)):
    name = await encode_name_utf7_ascii(name=mbox.name)
    try:
        status, response = await imap.delete(name)
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status == 'OK':
        return {'status': True, 'message': f"Папка {mbox.name} успешно удалена"}
    else:
        return {'status': False, 'message': f"Не удалось удалить папку {mbox.name}"}


@api_v1.post("/rename_folder",
             openapi_extra=rename_folder_request_example,
             response_model=Default200Response,
             responses=rename_folder_response_example,
             tags=['Folders'],
             summary=tags_description_api['rename_folder']['summary'],
             description=tags_description_api['rename_folder']['description']
             )
async def rename_folder(mbox: RenameFolder, imap=Depends(get_imap_connection)):
    old_name_folder = await encode_name_utf7_ascii(name=mbox.old_name_mbox)
    new_name_folder = await encode_name_utf7_ascii(name=mbox.new_name_mbox)
    try:
        status, response = await imap.rename(old_name_folder, new_name_folder)
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
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
    folder = await encode_name_utf7_ascii(name=mbox)
    try:
        status, _ = await imap.select(folder)
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        raise HTTPExceptionMail.FOLDER_NOT_FOUND_404

    status, response = await imap.uid("FETCH", uid, "(BODY[HEADER] BODY[1.MIME] BODY[1] BODYSTRUCTURE)")
    if status != 'OK':
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if len(response) == 1:
        raise HTTPExceptionMail.MESSAGE_NOT_FOUND_404

    message_header = email.message_from_bytes(response[1])
    subject = await get_decode_header_subject(message=message_header)
    body_header = email.message_from_bytes(response[3])
    # print('body_header', body_header)
    # print(message)
    body = response[5].decode()
    # print('body_start', body)
    if body_header.get('Content-Transfer-Encoding') == 'base64':
        body = base64.b64decode(body)
        body = body.decode()
    # print('end', body)
    attachments = await get_name_attachments(bodystructure=response[6])

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
        raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
    if status != 'OK':
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    return await parse_status_response(response=response[0])


# \\Flagged
@api_v1.get("/mark_read",
            response_model=Default200Response,
            responses=status_flags_response_example,
            tags=['Flags'],
            summary=tags_description_api['mark_read']['summary'],
            description=tags_description_api['mark_read']['description'])
async def mark_read_unread(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        uid: str = Query(..., description="UID письма", example="989"),
        flag: bool = Query(..., description=""),
        imap=Depends(get_imap_connection)):
    folder = await encode_name_utf7_ascii(name=mbox)
    try:
        status, _ = await imap.select(folder)
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
    if flag:
        status, response = await imap.uid("STORE", uid, "+FLAGS", f"({EmailFlags.flags['seen']})")
        if status != 'OK':
            raise HTTPExceptionMail.IMAP_TIMEOUT_504
        if len(response) == 1:
            return {'status': False, 'message': 'Сообщение и так не прочитано'}
    else:
        status, response = await imap.uid("STORE", uid, "-FLAGS", f"({EmailFlags.flags['seen']})")
        if status != 'OK':
            raise HTTPExceptionMail.IMAP_TIMEOUT_504
        if len(response) == 1:
            return {'status': False, 'message': 'Сообщение уже было прочитано'}
    return {'status': True, 'message': 'Статус сообщения изменен'}


@api_v1.get("/mark_flagged",
            response_model=Default200Response,
            responses=status_flags_response_example,
            tags=['Flags'],
            summary=tags_description_api['mark_flagged']['summary'],
            description=tags_description_api['mark_flagged']['description'])
async def mark_read_unread(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        uid: str = Query(..., description="UID письма", example="989"),
        flag: bool = Query(..., description=""),
        imap=Depends(get_imap_connection)):
    folder = await encode_name_utf7_ascii(name=mbox)
    try:
        status, _ = await imap.select(folder)
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
    if flag:
        status, response = await imap.uid("STORE", uid, "+FLAGS", f"({EmailFlags.flags['flagged']})")
        if status != 'OK':
            raise HTTPExceptionMail.IMAP_TIMEOUT_504
        if len(response) == 1:
            return {'status': False, 'message': 'Флаг уже был установлен'}
    else:
        status, response = await imap.uid("STORE", uid, "-FLAGS", f"({EmailFlags.flags['flagged']})")
        if status != 'OK':
            raise HTTPExceptionMail.IMAP_TIMEOUT_504
        if len(response) == 1:
            return {'status': False, 'message': 'Флаг уже был снят'}
    return {'status': True, 'message': 'Флаг изменен'}


@api_v1.post("/move_email",
             response_model=Default200Response,
             responses=move_emails_response_example,
             openapi_extra=move_mail_request_example,
             tags=['Moves, Copies, Deletes mails'],
             summary=tags_description_api['move_mail']['summary'],
             description=tags_description_api['move_mail']['description']
             )
async def move_email(
        move_emails: MoveEmails,
        imap=Depends(get_imap_connection)):
    try:
        encoded_source = await encode_name_utf7_ascii(name=move_emails.source_folder)
        encoded_target = await encode_name_utf7_ascii(name=move_emails.target_folder)
    except Exception:
        raise HTTPExceptionMail.ERROR_CODING_FOLDER_400
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
            raise HTTPExceptionMail.MOVING_COPY_MESSAGE_ERROR_409
        return {
            "status": True,
            "message": f"Письмо(а) {move_emails.uid} успешно перемещены из '{move_emails.source_folder}' в '{move_emails.target_folder}'",
        }
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    except Exception:
        raise HTTPExceptionMail.ERROR_IN_BACKEND_SERVER_500


@api_v1.post("/copy_email",
             response_model=Default200Response,
             responses=copy_emails_response_example,
             openapi_extra=copy_mail_request_example,
             tags=['Moves, Copies, Deletes mails'],
             summary=tags_description_api['copy_mail']['summary'],
             description=tags_description_api['copy_mail']['description']
             )
async def copy_email(
        copy_emails: CopyEmails,
        imap=Depends(get_imap_connection)):
    try:
        encoded_source = await encode_name_utf7_ascii(name=copy_emails.source_folder)
        encoded_target = await encode_name_utf7_ascii(name=copy_emails.target_folder)
    except Exception:
        raise HTTPExceptionMail.ERROR_CODING_FOLDER_400
    try:
        status, _ = await imap.select(encoded_source)
        if status != 'OK':
            raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                                detail=f"Исходная папка '{copy_emails.source_folder}' не найдена")

        # status, response = await imap.uid('COPY', uid, encoded_target)
        if isinstance(copy_emails.uid, list):
            uid_str = ",".join(copy_emails.uid)
        else:
            uid_str = copy_emails.uid
        status, response = await imap.uid('COPY', uid_str, encoded_target)
        if status != 'OK':
            raise HTTPExceptionMail.MOVING_COPY_MESSAGE_ERROR_409
        return {
            "status": True,
            "message": f"Письмо(а) {copy_emails.uid} успешно скопированы из '{copy_emails.source_folder}' в '{copy_emails.target_folder}'",
        }

    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    except Exception:
        raise HTTPExceptionMail.ERROR_IN_BACKEND_SERVER_500


# API в разработке и в тесте, 90% что уйдет в celery
@api_v1.get("/download_attachment/",
            # response_model=BodyResponse,
            # responses=body_message_response_example,
            tags=['Donwload attachment'],
            summary=tags_description_api['download_attachment']['summary'],
            description=tags_description_api['download_attachment']['description'])
async def download_attachment(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        uid: str = Query(..., description="UID письма", example="989"),
        part: int = Query(..., description=""),
        base64_status: bool = Query(True, description=""),
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

    # status, response = await imap.uid("FETCH", uid, "(BODY[HEADER] BODY[1.MIME] BODY[1] BODYSTRUCTURE)")
    try:
        status, response = await imap.uid("FETCH", uid, f"(BODY.PEEK[{part + 2}] BODYSTRUCTURE) ")
    except Exception as e:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if len(response) == 1:
        raise HTTPExceptionMail.MESSAGE_NOT_FOUND_404
    if base64_status:
        file = base64.b64decode(response[1])
    else:
        file = response[1].decode('ascii').strip()
    if len(file) == 0:
        raise HTTPExceptionMail.FILE_NOT_FOUND_404
    attachments = await get_name_attachments(response[2])
    chunk_size = 1024 * 1024

    filename = attachments[part]["filename"]
    # fallback — безопасное ASCII-имя
    ascii_fallback = re.sub(r'[^\x20-\x7E]', '_', filename)
    # RFC 5987-encoded имя
    filename_star = f"UTF-8''{urllib.parse.quote(filename, encoding='utf-8')}"
    mime_type, _ = mimetypes.guess_type(ascii_fallback)
    mime_type = mime_type or 'application/octet-stream'

    async def generate_chunk(chunk_size):
        for i in range(0, len(file), chunk_size):
            yield file[i:i + chunk_size]

    return StreamingResponse(
        generate_chunk(chunk_size),
        media_type=f'{mime_type}',
        headers={
            "Content-Disposition": f"attachment; filename=\"{ascii_fallback}\"; filename*= {filename_star}",
            "Cache-Control": "no-store",
            "Content-Type": f"{mime_type}",
            "X-Accel-Buffering": "no",
            "Content-Length": str(len(file))
        }
    )


@api_v1.post("/put_in_drafts",
             tags=['Moves, Copies, Deletes mails'],
             summary=tags_description_api['put_in_drafts']['summary'],
             description=tags_description_api['put_in_drafts']['description']
             )
async def put_in_draft(email_send: EmailSend,
                       background_tasks: BackgroundTasks,
                       imap=Depends(get_imap_connection)):
    message = await create_email_with_attachments(email_send)
    try:
        return Response(status_code=status_code.HTTP_200_OK,
                        background=background_tasks.add_task(append_inbox_message_in_drafts, message, imap))
    except Exception:
        raise HTTPExceptionMail.SMTP_TOO_MANY_REQUESTS_429


@api_v1.post("/delete_mails",
             tags=['Moves, Copies, Deletes mails'],
             summary=tags_description_api['delete_mail']['summary'],
             description=tags_description_api['delete_mail']['description']
             )
async def delete_mails(uids_mails: UidsMails,
                       imap=Depends(get_imap_connection)):
    try:
        status, _ = await imap.select('Trash')
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
    if uids_mails.uids:
        status, response = await imap.uid('STORE', ','.join(uids_mails.uids), '+FLAGS.SILENT', '(\\Deleted)')
        if status != 'OK':
            raise HTTPExceptionMail.ERROR_DELETES_MAILS
        await imap.expunge()
        return {'status': True, 'message': 'Выбранные сообщения удалены из корзины'}
    if uids_mails.clear_all_trash is True:
        status_all, messages = await imap.uid_search("ALL")
        if status_all != 'OK':
            raise HTTPExceptionMail.IMAP_TIMEOUT_504
        uids = messages[0].decode().split()
        status, response = await imap.uid('STORE', ','.join(uids), '+FLAGS.SILENT', '(\\Deleted)')
        if status != 'OK':
            raise HTTPExceptionMail.ERROR_DELETES_MAILS
        await imap.expunge()
        return {'status': True, 'message': 'Все сообщения удалены из корзины'}
