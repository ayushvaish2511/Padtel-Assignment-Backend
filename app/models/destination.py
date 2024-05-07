# schemas.py

from pydantic import BaseModel
from typing import List, Dict

class DestinationBase(BaseModel):
    url: str
    http_method: str
    headers: Dict[str, str]

class DestinationCreate(DestinationBase):
    account_id: int

class DestinationUpdate(DestinationBase):
    pass

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