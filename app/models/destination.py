# schemas.py

from pydantic import BaseModel
from typing import List, Dict, Optional

class DestinationBase(BaseModel):
    url: str
    http_method: str
    headers: Dict[str, str]

class DestinationCreate(DestinationBase):
    account_id: int

class DestinationUpdate(BaseModel):
    url: Optional[str]
    http_method: Optional[str]
    headers: Optional[Dict[str, str]]

class Destination(DestinationBase):
    destination_id: int
    account_id: int

    class Config:
        orm_mode = True

class DestinationResponse(BaseModel):
    DESTINATION_ID: int
    URL: str 
    HTTP_METHOD: str 
    HEADERS: str 
    ACCOUNT_ID: int 

class Message(BaseModel):
    message: str