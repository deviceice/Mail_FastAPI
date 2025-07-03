import logging
import time
import urllib.parse
import uuid
import aiofiles.os

from fastapi import (APIRouter, HTTPException, Response, BackgroundTasks, Depends, Query)
from fastapi.responses import StreamingResponse
from starlette import status as status_code

from mail.example_schemas.request_schemas_examples import *
from mail.example_schemas.response_schemas_examples import *
from mail.imap_smtp_connect.imap_connection import get_imap_connection
from mail.imap_smtp_connect.smtp_connection import get_smtp_connection
from mail.options_emails import EmailFlags
from mail.schemas.request.schemas_mail_req import *
from mail.schemas.response.schemas_mail_res import *
from mail.schemas.tags_api import tags_description_api
from mail.utils_func_API import *
from tests.pam_auth import pam_auth

api_v1 = APIRouter(prefix="/api/v1", dependencies=[Depends(pam_auth)])
BASE_DIR_APP = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR_APP / 'temp'
semaphore_upload_files = asyncio.Semaphore(50)


@api_v1.get('/mails',
            response_model=GetMailsResponse,
            responses=get_mails_response_example,
            tags=['Get mails'],
            summary=tags_description_api['mails']['summary'],
            description=tags_description_api['mails']['description']
            )
async def get_mails(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        limit: Optional[int] = Query(20, description="Количество писем для получения (от 1 до 100)",
                                     ge=1, le=1000),
        last_uid: Optional[str] = Query(None,
                                        description="Последний UID корневого письма, после которого прислать "
                                                    "следующие письма"),
        imap=Depends(get_imap_connection)):
    try:
        folder = encode_name_imap_utf7(mbox)
        status_list, response_folders = await imap.list('""', '"*"')
        status_select_folder, _ = await imap.select(f'"{folder}"')
        status_thread, thread_response = await imap.uid('THREAD', 'REFS UTF-8 ALL')
        if status_list != 'OK' or status_select_folder != 'OK':
            raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
        if status_thread != 'OK':
            raise HTTPExceptionMail.IMAP_TIMEOUT_504

        all_folders: Optional[list[str]] = await parse_folders(response_folders) if status_list == 'OK' else None
        thread_tree = parse_thread_response(thread_response[0])
        root_threads = get_root_threads_slice(thread_tree, limit, last_uid)
        uids_to_fetch_lists = [flatten_thread(thread) for thread in root_threads]
        uids_to_fetch = sorted({uid for sublist in uids_to_fetch_lists for uid in sublist})

        if not uids_to_fetch:
            return {'status': True, 'total_message': 0, 'total_unseen_message': 0, 'folders': all_folders, 'emails': []}

        status_all, messages = await imap.uid_search("ALL")
        status_unread, messages_unseen = await imap.uid_search("UNSEEN")
        if status_all != 'OK' and status_unread != 'OK':
            raise HTTPExceptionMail.IMAP_TIMEOUT_504

        mails_uids_all, mails_uids_unseen, total_message, total_unseen_message = get_mails_uids_unseen(
            messages=messages,
            messages_unseen=messages_unseen)

        if not mails_uids_all:
            return {'status': False, 'total_message': total_message, 'total_unseen_message': total_unseen_message,
                    'folders': all_folders, 'emails': []}

        status, msg_data_bytes = await imap.uid("FETCH", ",".join(map(str, uids_to_fetch)),
                                                "(FLAGS RFC822.HEADER BODYSTRUCTURE)")
        if status != 'OK':
            return {'status': False, 'total_message': total_message, 'total_unseen_message': total_unseen_message,
                    'folders': all_folders, 'emails': []}

        msg_data, options_message, _ = await asyncio.to_thread(clear_bytes_in_message, message=msg_data_bytes)
        parsed_messages = await asyncio.gather(
            *[asyncio.to_thread(email.message_from_bytes, msg_bytes) for msg_bytes in msg_data])
        messages_dict = {}

        for mail_uid, message, options in zip(uids_to_fetch, parsed_messages, options_message):
            main_message = get_message_struct(
                mail_uid=mail_uid,
                mails_uids_unseen=mails_uids_unseen,
                message=message,
                options=options
            )
            messages_dict[mail_uid] = main_message

        mails = build_email_tree_by_references(messages_dict)
        mails.sort(key=get_max_uid_in_thread, reverse=True)

        return {'status': True, 'total_message': total_message, 'total_unseen_message': total_unseen_message,
                'folders': all_folders, 'emails': mails}
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504


@api_v1.get('/mail',
            response_model=GetMailResponse,
            responses=get_mail_response_example,
            tags=['Get mails'],
            summary=tags_description_api['mail']['summary'],
            description=tags_description_api['mail']['description']
            )
async def get_mail(
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        number: Optional[str] = Query(...,
                                      description="Порядковый номер письма, которое прислать"),
        imap=Depends(get_imap_connection)):
    try:
        folder = encode_name_imap_utf7(mbox)
        status, response = await imap.select(f'"{folder}"')
        if status != 'OK':
            raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
        status, msg_data_bytes = await imap.fetch(number, "(UID FLAGS RFC822.HEADER BODYSTRUCTURE)")
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        return {'status': False, 'mail': None}
    main_message = await asyncio.to_thread(get_new_mail, msg_data_bytes)
    return {'status': True, 'mail': main_message}


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
    folder = encode_name_imap_utf7(mbox)
    try:
        status, _ = await imap.select(f'"{folder}"')
        if status != 'OK':
            raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
        status_recent, messages_recent = await imap.uid_search("RECENT")
        if status_recent != 'OK':
            raise HTTPExceptionMail.IMAP_TIMEOUT_504

        mails_uids_recents, total_message_recent = await get_mails_uids_recent(messages_recent=messages_recent)
        status, msg_data_bytes = await imap.uid("FETCH", ",".join(mails_uids_recents),
                                                "(FLAGS RFC822.HEADER BODYSTRUCTURE)")
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        return {'status': False, 'total_message': total_message_recent, 'emails': []}
    emails_list = []
    msg_data, options_messages, _ = await asyncio.to_thread(clear_bytes_in_message, message=msg_data_bytes)

    for mail_uid, message, options in zip(mails_uids_recents, msg_data, options_messages):
        message = email.message_from_bytes(message)
        main_message = get_message_struct(mail_uid=mail_uid, message=message,
                                          options=options, mails_uids_unseen=None)
        emails_list.append(main_message)
    emails_list.reverse()
    return {'status': True, 'total_message_recent': total_message_recent, 'emails': emails_list}


# API в доработке, отправка будет осуществляться через celery
@api_v1.post("/send_mail",
             openapi_extra=send_mail_request_example,
             tags=['Send mails'],
             summary=tags_description_api['send_mail']['summary'],
             description=tags_description_api['send_mail']['description']
             )
async def send_emails(email_send: EmailSend,
                      background_tasks: BackgroundTasks,
                      mail_login=Depends(get_mail_login_pam),
                      smtp=Depends(get_smtp_connection),
                      imap=Depends(get_imap_connection)):
    if mail_login is None:
        raise HTTPExceptionMail.NOT_AUTHENTICATED_401

    message = await create_email_with_attachments(email_send, mail_login)
    logger.info(f"Создалось сообщение")
    try:
        status, response = await smtp.send_message(message)
        logger.info(f"отправлено {status}, {response}")
        # await imap.append(message_bytes=message.as_bytes(), mailbox='Sent', flags=EmailFlags.flags['seen'])
        # logger.info("Добавлено в отправленные")
        return Response(status_code=status_code.HTTP_200_OK, )
        # background=background_tasks.add_task(append_inbox_message_in_sent, message, imap))
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
        # folders = await parse_folders(response)
        return {'status': True, 'folders': await parse_folders(response)}
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
    name = encode_name_imap_utf7(mbox.name)
    try:
        status, response = await imap.create(f'"{name}"')
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
    name = encode_name_imap_utf7(mbox.name)
    try:
        status, response = await imap.delete(f'"{name}"')
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
    old_name_folder = encode_name_imap_utf7(mbox.old_name_mbox)
    new_name_folder = encode_name_imap_utf7(mbox.new_name_mbox)
    try:
        status, response = await imap.rename(f'"{old_name_folder}"', f'"{new_name_folder}"')
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
    folder = encode_name_imap_utf7(mbox)
    try:
        status, _ = await imap.select(f'"{folder}"')
        if status != 'OK':
            raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
        status, response = await imap.uid("FETCH", uid, "(BODY[HEADER] BODY[1.MIME] BODY[1] BODYSTRUCTURE)")
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if len(response) == 1:
        raise HTTPExceptionMail.MESSAGE_NOT_FOUND_404

    message_header = email.message_from_bytes(response[1])
    subject = get_decode_header_subject(message=message_header)
    body_header = email.message_from_bytes(response[3])
    body = response[5].decode()
    if body_header.get('Content-Transfer-Encoding') == 'base64':
        body = base64.b64decode(body)
        body = body.decode()
    attachments = await get_name_attachments(bodystructure=response[6])
    return {
        'status': True,
        "uid": uid,
        "from": message_header["From"] if message_header["From"] else '',
        'to': message_header['To'].split(',') if message_header['To'] else [],
        "subject": subject if subject else '',
        "date": message_header["Date"] if message_header['Date'] else '',
        "body": body if body else '',
        'attachments': attachments
    }


@api_v1.get("/status_folder",
            # response_model=StatusFolderResponse,
            # responses=status_folder_response_example,
            tags=['Status folder'],
            summary=tags_description_api['status_folder']['summary'],
            description=tags_description_api['status_folder']['description'])
async def status_folder(
        imap=Depends(get_imap_connection)):
    try:
        status, response = await imap.list('""', '"*"')
        if status != 'OK':
            raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
        all_folders: Optional[list[str]] = await parse_folders(response) if status == 'OK' else None
        data_folders = {}
        for folder in all_folders:
            folder = encode_name_imap_utf7(folder)
            status, response = await imap.status(f'"{folder}"', '(MESSAGES UNSEEN RECENT)')
            parsed_data = await parse_status_folders_response(response=response[0])
            data_folders[decode_name_imap_utf7(folder)] = parsed_data

    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status == 'NO':
        raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
    if status != 'OK':
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    return data_folders


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
    folder = encode_name_imap_utf7(mbox)
    try:
        status, _ = await imap.select(f'"{folder}"')
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
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
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
    folder = encode_name_imap_utf7(mbox)
    try:
        status, _ = await imap.select(f'"{folder}"')

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
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
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
        move_emails: MoveMails,
        imap=Depends(get_imap_connection)):
    try:
        encoded_source = encode_name_imap_utf7(move_emails.source_folder)
        encoded_target = encode_name_imap_utf7(move_emails.target_folder)
    except Exception:
        raise HTTPExceptionMail.ERROR_CODING_FOLDER_400
    try:
        status, _ = await imap.select(f'"{encoded_source}"')
        if status != 'OK':
            raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                                detail=f"Исходная папка '{move_emails.source_folder}' не найдена")
        if isinstance(move_emails.uid, list):
            uid_str = ",".join(move_emails.uid)
        else:
            uid_str = move_emails.uid
        status, response = await imap.uid('MOVE', uid_str, f'"{encoded_target}"')
        if status != 'OK':
            raise HTTPExceptionMail.MOVING_COPY_MESSAGE_ERROR_409
        return {
            "status": True,
            "message": f"Письмо(а) {move_emails.uid} успешно перемещены "
                       f"из '{move_emails.source_folder}' в '{move_emails.target_folder}'",
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
        copy_emails: CopyMails,
        imap=Depends(get_imap_connection)):
    try:
        encoded_source = encode_name_imap_utf7(copy_emails.source_folder)
        encoded_target = encode_name_imap_utf7(copy_emails.target_folder)
    except Exception:
        raise HTTPExceptionMail.ERROR_CODING_FOLDER_400
    try:
        status, _ = await imap.select(f'"{encoded_source}"')
        if status != 'OK':
            raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                                detail=f"Исходная папка '{copy_emails.source_folder}' не найдена")

        # status, response = await imap.uid('COPY', uid, encoded_target)
        if isinstance(copy_emails.uid, list):
            uid_str = ",".join(copy_emails.uid)
        else:
            uid_str = copy_emails.uid
        status, response = await imap.uid('COPY', uid_str, f'"{encoded_target}"')
        if status != 'OK':
            raise HTTPExceptionMail.MOVING_COPY_MESSAGE_ERROR_409
        return {
            "status": True,
            "message": f"Письмо(а) {copy_emails.uid} успешно скопированы "
                       f"из '{copy_emails.source_folder}' в '{copy_emails.target_folder}'",
        }

    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    except Exception:
        raise HTTPExceptionMail.ERROR_IN_BACKEND_SERVER_500


@api_v1.get("/download_attachment",
            # response_model=BodyResponse,
            # responses=body_message_response_example,
            tags=['Donwload attachment'],
            summary=tags_description_api['download_attachment']['summary'],
            description=tags_description_api['download_attachment']['description'])
async def download_attachment(
        background_tasks: BackgroundTasks,
        mbox: str = Query(..., description="Название папки в почтовом ящике", example="INBOX"),
        uid: str = Query(..., description="UID письма", example="989"),
        part: int = Query(..., description=""),
        base64_status: bool = Query(True, description=""),
        imap=Depends(get_imap_connection)
):
    folder = encode_name_imap_utf7(mbox)
    try:
        status, _ = await imap.select(f'"{folder}"')
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
    try:
        status, response_body_struct = await imap.uid("FETCH", uid, f"(BODYSTRUCTURE)")
    except Exception:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if status != 'OK':
        raise HTTPExceptionMail.IMAP_TIMEOUT_504
    if len(response_body_struct) == 1:
        raise HTTPExceptionMail.MESSAGE_NOT_FOUND_404

    attachments = await get_name_attachments(response_body_struct[0])
    try:
        filename = attachments[part]["filename"]
    except IndexError:
        raise HTTPExceptionMail.FILE_NOT_FOUND_404
    ascii_fallback = re.sub(r'[^\x20-\x7E]', '_', filename)
    filename_star = f"UTF-8''{urllib.parse.quote(filename, encoding='utf-8')}"
    mime_type, _ = mimetypes.guess_type(ascii_fallback)
    mime_type = mime_type or 'application/octet-stream'

    CHUNK_SIZE = 1024 * 16  # 64KB
    # CHUNK_SIZE = 1024 * 64  # 64KB
    offset = 0
    fetched_data = bytearray()
    start = datetime.now()
    # 1с на 6,6 мб

    while True:
        fetch_cmd = f"BODY.PEEK[{part + 2}]<{offset}.{CHUNK_SIZE}>"
        status, chunk_resp = await imap.uid("FETCH", uid, f"({fetch_cmd})")
        await asyncio.sleep(0)
        if status != "OK":
            raise HTTPExceptionMail.IMAP_TIMEOUT_504

        # chunk_resp[0] должен содержать данные
        chunk_data = chunk_resp[1] if isinstance(chunk_resp[1], tuple) else chunk_resp[1]
        if not chunk_data:
            break  # конец данных

        fetched_data += chunk_data
        if len(chunk_data) < CHUNK_SIZE:
            break  # последняя часть

        offset += CHUNK_SIZE

    end = datetime.now()
    print('time download file imap end=', end - start)
    temp_path = await async_chunked_base64_to_temp(fetched_data)
    print('base64 end')

    file_size = os.path.getsize(temp_path)

    async def file_sender(file_path: str):
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                while True:
                    chunk = await f.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            logging.error(f"Error streaming file {file_path}: {str(e)}")
            raise

    return StreamingResponse(
        file_sender(temp_path),
        media_type=f'{mime_type}',
        headers={
            "Content-Disposition": f"attachment; filename=\"{ascii_fallback}\"; filename*= {filename_star}",
            "Cache-Control": "private, max-age=0, no-cache",
            "Content-Type": f"{mime_type}",
            "Accept-Ranges": "bytes",
            "X-Accel-Buffering": "no",
            "Content-Length": str(file_size),
            "Connection": "keep-alive"
        },
        background=background_tasks.add_task(delete_temp_file, temp_path)
    )


@api_v1.post("/put_in_drafts",
             tags=['Moves, Copies, Deletes mails'],
             summary=tags_description_api['put_in_drafts']['summary'],
             description=tags_description_api['put_in_drafts']['description']
             )
async def put_in_draft(email_send: EmailSend,
                       background_tasks: BackgroundTasks,
                       mail_login=Depends(get_mail_login_pam),
                       imap=Depends(get_imap_connection)):
    if mail_login is None:
        raise HTTPExceptionMail.NOT_AUTHENTICATED_401
    message = await create_email_with_attachments(email_send, mail_login)
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
async def delete_mails(
        uids_mails: DeleteMails,
        imap=Depends(get_imap_connection)):
    try:
        folder = encode_name_imap_utf7(uids_mails.mbox)
        status, response = await imap.select(f'"{folder}"')

        if status != 'OK':
            raise HTTPExceptionMail.FOLDER_NOT_FOUND_404
        if uids_mails.uids:
            status, _ = await imap.uid('STORE', ','.join(uids_mails.uids), '+FLAGS.SILENT', EmailFlags.flags['deleted'])
            if status != 'OK':
                raise HTTPExceptionMail.ERROR_DELETES_MAILS_304
            await imap.expunge()
            return {'status': True, 'message': f'Выбранные сообщения удалены из {uids_mails.mbox}'}
        if uids_mails.clear_all_trash is True:
            status_all, messages = await imap.uid_search("ALL")
            if status_all != 'OK':
                raise HTTPExceptionMail.IMAP_TIMEOUT_504
            status, _ = await imap.uid('STORE', ','.join(messages[0].decode().split()), '+FLAGS.SILENT',
                                       EmailFlags.flags['deleted'])
            if status != 'OK':
                raise HTTPExceptionMail.ERROR_DELETES_MAILS_304
            await imap.expunge()
        return {'status': True, 'message': f'Все сообщения удалены из {uids_mails.mbox}'}
    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504


@api_v1.get('/search_mails',
            response_model=GetMailsSearch,
            responses=get_mails_search_example,
            tags=['Get mails'],
            summary="Поиск почтовых сообщений по фильтрам",
            description="Поиск почтовых сообщений по теме, отправителю, дате или по содержимому")
async def search_mails(
        mbox: str = Query(..., description="Mailbox folder", example="INBOX"),
        subject: Optional[str] = Query(None, description="Тема"),
        from_: Optional[str] = Query(None, alias="from", description="От кого"),
        since_date: Optional[str] = Query(None, description="Дата (DD.MM.YYYY)"),
        body: Optional[str] = Query(None, description="Содержимое"),
        limit: Optional[int] = Query(50, ge=1, le=100, description="Отрезок кол-ва возвращаемых сообщений"),
        last_uid: Optional[str] = Query(None, description="Последний UID письма, после которого "
                                                          "прислать следующие письма"),
        imap=Depends(get_imap_connection)
):
    try:

        folder = encode_name_imap_utf7(mbox)
        status_select_folder, _ = await imap.select(f'"{folder}"')
        if status_select_folder != 'OK':
            raise HTTPExceptionMail.FOLDER_NOT_FOUND_404

        search_criteria = []

        if subject and from_:
            search_criteria = ['OR', f'SUBJECT "{subject}"', f'FROM "{from_}"']
        elif subject:
            search_criteria += ['SUBJECT', f'"{subject}"']
        elif from_:
            search_criteria += ['FROM', from_]
        elif since_date:
            date_obj = datetime.strptime(since_date, "%d.%m.%Y")
            search_criteria += ['SINCE', date_obj.strftime("%d-%b-%Y")]
        elif body:
            search_criteria += ['BODY', f'"{body}"']
        if not search_criteria:
            search_criteria = ['ALL']

        status_search, messages = await imap.uid_search(*search_criteria)
        status_unread, messages_unseen = await imap.uid_search("UNSEEN")
        if status_search != 'OK' or status_unread != 'OK':
            raise HTTPExceptionMail.IMAP_TIMEOUT_504
        mails_uids_search, mails_uids_unseen, total_message, total_unseen_message = get_mails_uids_unseen(
            messages=messages,
            messages_unseen=messages_unseen)
        if not mails_uids_search:
            return {'status': True, 'total_search': 0, 'mails': []}
        mails_uids_search = get_elements_inbox_uid(mails_uids_search, last_uid, limit if limit else 20)
        status_search, msg_data_bytes = await imap.uid("FETCH", ",".join(mails_uids_search),
                                                       "(FLAGS RFC822.HEADER BODYSTRUCTURE)")
        if status_search != 'OK':
            return {'status': False, 'total_search': len(mails_uids_search), 'emails': []}
        msg_data, options_message, _ = await asyncio.to_thread(clear_bytes_in_message, message=msg_data_bytes)
        parsed_messages = await asyncio.gather(
            *[asyncio.to_thread(email.message_from_bytes, msg_bytes) for msg_bytes in msg_data])
        messages_dict = {}
        for mail_uid, message, options in zip(mails_uids_search, parsed_messages, options_message):
            main_message = get_message_struct(
                mail_uid=mail_uid,
                mails_uids_unseen=mails_uids_unseen,  # Можно получить статус UNSEEN, если нужно
                message=message,
                options=options
            )
            messages_dict[mail_uid] = main_message

        mails = build_email_tree_by_references(messages_dict)
        mails.sort(key=get_max_uid_in_thread, reverse=True)
        return {'status': True, 'total_search': len(mails_uids_search), 'mails': mails}

    except asyncio.exceptions.TimeoutError:
        raise HTTPExceptionMail.IMAP_TIMEOUT_504


@api_v1.post("/upload_attachments", tags=["Upload attachment"])
async def upload_attachments(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        file_id = str(uuid.uuid4())
        save_path = UPLOAD_DIR / file_id
        try:
            async with semaphore_upload_files:
                async with aiofiles.open(save_path, "wb") as out_file:
                    while content := await file.read(1024 * 1024):
                        await out_file.write(content)

            results.append({
                "id": file_id,
                "filename": file.filename,
            })
        except Exception:
            raise HTTPExceptionMail.ERROR_SAVED_FILE_400

    return {"files": results}


@api_v1.post("/delete_attachments", tags=["Upload attachment"])
async def delete_attachments(files: List[str]):
    deleted = []
    not_found = []
    for file_uuid in files:
        file_path = UPLOAD_DIR / file_uuid
        if file_path.exists():
            try:
                await aiofiles.os.remove(file_path)
                deleted.append(file_uuid)
            except Exception:
                not_found.append(file_uuid)
        else:
            not_found.append(file_uuid)
    return {
        "deleted": deleted,
        "not_found": not_found
    }
