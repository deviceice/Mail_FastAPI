from pydantic import BaseModel, EmailStr, Field
from typing import Union, Optional, List, Dict, Sequence

from pydantic import BaseModel


class Attachment(BaseModel):
    filename: str
    size: str


class EmailReferanse(BaseModel):
    uid: str
    message_id: str
    from_: str = Field(alias="from")
    to: List[str] = []
    subject: str
    date: str
    is_read: bool
    # mails_referance: list[str] = []
    flags: bool
    attachments: List[Attachment] = []


class Email(BaseModel):
    uid: str
    message_id: str
    from_: str = Field(alias="from")
    to: List[str] = []
    subject: str
    date: str
    is_read: bool
    flags: bool
    attachments: List[Attachment] = []
    mails_referance: List[EmailReferanse] = []


class GetMailsResponse(BaseModel):
    status: bool
    total_message: int = 0
    folders: list[str]
    emails: List[Email] = []
