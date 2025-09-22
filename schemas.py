from pydantic import BaseModel
from typing import Optional, List

# --- NewsArticle Schemas ---
class NewsArticleBase(BaseModel):
    title: str
    content: str

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticle(NewsArticleBase):
    id: int
    author_id: int

    class Config:
        # Corrected from 'orm_mode' to 'from_attributes' for Pydantic V2
        from_attributes = True

# --- User Schemas ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(BaseModel):
    id: int
    email: str
    is_active: bool
    articles: List[NewsArticle] = []

    class Config:
        # Corrected from 'orm_mode' to 'from_attributes' for Pydantic V2
        from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

