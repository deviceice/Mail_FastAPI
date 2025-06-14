import email
import re
from mail.utils_func_API.utils_mails import *


def get_new_mail(msg_data_bytes):
    message_msg, options, uid = clear_bytes_in_message(msg_data_bytes)
    message = email.message_from_bytes(message_msg[0])
    main_message = get_message_struct(mail_uid=uid, mails_uids_unseen=None,
                                      message=message, options=options[0])
    return main_message
