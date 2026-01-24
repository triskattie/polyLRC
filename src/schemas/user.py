from pydantic import BaseModel, EmailStr, Field
import re


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)