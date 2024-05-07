from pydantic import BaseModel, EmailStr
from typing import Optional

class AccountBase(BaseModel):
    email: EmailStr
    account_name: str
    website: Optional[str] = None

class AccountCreate(BaseModel):
    email: EmailStr
    account_name: str
    website: Optional[str] = None

class AccountUpdate(BaseModel):
    email: Optional[EmailStr]
    account_name: Optional[str]
    website: Optional[str] = None

class Account(BaseModel):
    email: str
    account_name: str
    app_secret_token: str
    website: Optional[str] = None

    class Config:
        orm_mode = True
        exclude = ['account_id'] 

class AccountReturn(BaseModel):
    ACCOUNT_ID: int
    EMAIL: str
    ACCOUNT_NAME: str 
    APP_SECRET_TOKEN: str 
    WEBSITE: str

class Message(BaseModel):
    message: str