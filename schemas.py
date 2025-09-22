from pydantic import BaseModel
from typing import Optional

# Pydantic models for News Articles
class NewsArticleBase(BaseModel):
    title: str
    content: str

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticle(NewsArticleBase):
    id: int
    author_id: int

    class Config:
        orm_mode = True

# Pydantic models for Users
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    articles: list[NewsArticle] = []

    class Config:
        orm_mode = True

# Pydantic models for Authentication
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

