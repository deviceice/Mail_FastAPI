from pydantic import BaseModel
from typing import Union, Optional, List, Dict, Sequence

from typing import Union


class AbonentOut(BaseModel):
    abonent_sid: int
    fio: Union[str, None]
    object_sid: int
    address: Union[int, None]
    login: Union[str, None] = None
    email: Union[str, None]
    object_name: Union[str, None]
    job_name: Union[str, None]

    class Config:
        from_attributes = True


class ObjectOut(BaseModel):
    object_sid: Union[int, None]
    parent_object_sid: Union[int, None]
    name: Union[str, None]
