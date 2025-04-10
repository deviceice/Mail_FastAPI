async def get_mails_uids_recent(messages_recent):
    mails_uids_recents = messages_recent[0].decode().split()
    total_message_recent = len(mails_uids_recents)
    return mails_uids_recents, total_message_recent
