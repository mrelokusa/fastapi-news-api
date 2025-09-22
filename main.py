from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import auth
from database import engine, get_db

# This command ensures that the database tables are created if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)):
    return current_user

@app.post("/articles/", response_model=schemas.NewsArticle, status_code=status.HTTP_201_CREATED)
def create_article(
    article: schemas.NewsArticleCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    # For simplicity, we'll assign the current user as the author.
    # In a real app, you might handle authoring differently.
    return auth.create_news_article(db=db, article=article, author_id=current_user.id)

@app.get("/articles/", response_model=List[schemas.NewsArticle])
def read_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = auth.get_news_articles(db, skip=skip, limit=limit)
    return articles

@app.get("/articles/{article_id}", response_model=schemas.NewsArticle)
def read_article(article_id: int, db: Session = Depends(get_db)):
    db_article = auth.get_news_article(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article

