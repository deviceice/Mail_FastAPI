from pydantic import BaseModel, EmailStr
from typing import Union, Optional, List, Dict, Sequence
from fastapi import UploadFile, File, Form


class Attachment(BaseModel):
    filename: str
    uuid: str

# class Attachment(BaseModel):
#     filename: str
#     file: List[UploadFile] = File([])


class EmailSend(BaseModel):
    to: Union[EmailStr, Sequence[EmailStr]]
    subject: str
    body: str
    reference: Optional[str] = None
    attachments: List[Attachment] = []
    # attachments: List[UploadFile] = File([])


class NameFolder(BaseModel):
    name: str


class RenameFolder(BaseModel):
    old_name_mbox: str
    new_name_mbox: str


class GetBodyMessage(BaseModel):
    mbox: str
    uid: str


class MoveMails(BaseModel):
    source_folder: str
    target_folder: str
    uid: Union[str, List[str]]


class CopyMails(BaseModel):
    source_folder: str
    target_folder: str
    uid: Union[str, List[str]]


class DeleteMails(BaseModel):
    mbox: str
    uids: Optional[List[str]] = None
    clear_all_trash: Optional[bool] = None
