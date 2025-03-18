from pydantic import BaseModel, EmailStr
from typing import Union, Optional, List, Dict, Sequence


class Attachment(BaseModel):
    filename: str
    file: str


class EmailSend(BaseModel):
    to: Union[EmailStr, Sequence[EmailStr]]
    subject: str
    body: str
    referance: Optional[str] = None
    attachments: List[Attachment] = []


class NameFolder(BaseModel):
    mbox: str


class RenameFolder(BaseModel):
    mbox: str
    new_box: str


class GetBodyMessage(BaseModel):
    mbox: str
    uid: str
