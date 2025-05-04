from mail.support_func_API import get_decode_header_subject


async def get_mails_uids_recent(messages_recent):
    mails_uids_recents = messages_recent[0].decode().split()
    total_message_recent = len(mails_uids_recents)
    return mails_uids_recents, total_message_recent


async def get_new_message_struct(mail_uid, message, options):
    return {
        "uid": mail_uid,
        "message_id": message.get("Message-ID", "").strip('<>'),
        "from": message["From"] if message["From"] else '',
        "to": message['To'].split(',') if message['To'] else '',
        "subject": await get_decode_header_subject(message),
        "date": message["Date"] if message["Date"] else '',
        "is_read": False,
        "flags": options['flags'] if mail_uid == options['uid'] else False,
        "attachments": options['attachments'] if mail_uid == options['uid'] else [],
        "mails_reference": [],
    }