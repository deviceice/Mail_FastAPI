from mail.support_func_API.support_func import *


async def append_inbox_message_in_sent(message, imap):
    await imap.append(message_bytes=message.as_bytes(), mailbox='Sent', flags='\\Seen', )


async def create_email_with_attachments(email: EmailSend):
    # создает MIMEMultipart сообщение с вложенными attachments либо без них
    message = MIMEMultipart()
    message["From"] = "user@mail.palas"  # жестко пока для теста
    message["To"] = email.to if type(email.to) == str else ", ".join(email.to)
    message["Subject"] = email.subject
    message["References"] = f'<{email.referance}>' if email.referance else None
    message.attach(MIMEText(email.body, "plain"))
    for attachment in email.attachments:
        part = MIMEBase("application", "octet-stream")
        decoded_data = base64.b64decode(attachment.file)
        part.set_payload(decoded_data)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={attachment.filename}; size={str(len(decoded_data))}"
        )
        message.attach(part)
    return message
