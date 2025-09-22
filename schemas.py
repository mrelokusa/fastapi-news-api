from pydantic import BaseModel
from typing import List, Optional

# News Article Schemas
class NewsArticleBase(BaseModel):
    title: str
    content: str

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticle(NewsArticleBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    is_admin: Optional[bool] = False

class User(UserBase):
    id: int
    is_admin: bool
    articles: List[NewsArticle] = []

    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
