from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Union, Optional, List, Dict, Sequence
from pydantic import BaseModel


class Attachment(BaseModel):
    filename: Union[str, None]
    size: Union[str, None]


class EmailReferense(BaseModel):
    uid: Union[str, int]
    message_id: Union[str, None]
    from_: str = Field(alias="from")
    to: List[str] = []
    subject: Union[str, None]
    date: Union[str, None]
    is_read: bool
    flags: bool
    references: Union[str, None]
    attachments: List[Attachment] = []
    mails_reference: list = []


class Email(BaseModel):
    uid: int
    message_id: Union[str, None]
    from_: str = Field(alias="from")
    to: List[str] = []
    subject: Union[str, None]
    date: Union[str, None]
    is_read: bool
    flags: bool
    attachments: List[Attachment] = []
    references: Union[str, None]  # if message.get("References", ""):
    # mails_reference: List[EmailReferense] = []


class GetMailsResponse(BaseModel):
    status: bool
    total_message: int = 0
    total_unseen_message: int = 0,
    # folders: list[str]
    emails: List[Email] = []


class GetMailsSearch(BaseModel):
    status: bool
    total_search: int = 0
    mails: List[Email] = []


class GetNewMailsResponse(BaseModel):
    status: bool
    total_message_recent: int = 0
    emails: List[Email] = []


class BodyResponse(BaseModel):
    status: bool
    uid: str
    from_: str = Field(alias="from")
    to: List[str] = []
    subject: str
    date: str
    body: str
    attachments: List[Attachment] = []


class Default200Response(BaseModel):
    status: bool
    message: str


class StatusFolderResponse(BaseModel):
    messages: int
    recent: int
    unseen: int
    key: str


class GetMailResponse(BaseModel):
    status: bool
    mail: Optional[Email] = None


class AttachmentSaved(BaseModel):
    uuid: UUID4
    filename: str
    size: int
