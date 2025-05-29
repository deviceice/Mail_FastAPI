from pydantic import BaseModel, EmailStr
from typing import Union, Optional, List, Dict, Sequence


class Attachment(BaseModel):
    filename: str
    file: str


class EmailSend(BaseModel):
    to: Union[EmailStr, Sequence[EmailStr]]
    subject: str
    body: str
    reference: Optional[str] = None
    attachments: List[Attachment] = []


class NameFolder(BaseModel):
    name: str


class RenameFolder(BaseModel):
    old_name_mbox: str
    new_name_mbox: str


class GetBodyMessage(BaseModel):
    mbox: str
    uid: str


class MoveEmails(BaseModel):
    source_folder: str
    target_folder: str
    uid: Union[str, List[str]]


class CopyEmails(BaseModel):
    source_folder: str
    target_folder: str
    uid: Union[str, List[str]]


class UidsMails(BaseModel):
    uids: Optional[List[str]] = None
    clear_all_trash: Optional[bool] = None
