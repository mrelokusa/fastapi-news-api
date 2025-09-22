from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import auth, models, schemas
from database import engine, get_db

# This command creates the database tables if they don't exist.
# We will use Alembic for production, but this is fine for initial setup.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Authentication Endpoints ---
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.get_user(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, is_admin=user.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# --- News Article CRUD Endpoints ---
@app.post("/news/", response_model=schemas.NewsArticle, status_code=status.HTTP_201_CREATED)
def create_news_article(
    article: schemas.NewsArticleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_article = models.NewsArticle(**article.model_dump(), owner_id=current_user.id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@app.get("/news/", response_model=List[schemas.NewsArticle])
def read_all_news_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = db.query(models.NewsArticle).offset(skip).limit(limit).all()
    return articles

@app.get("/news/{article_id}", response_model=schemas.NewsArticle)
def read_news_article(article_id: int, db: Session = Depends(get_db)):
    db_article = db.query(models.NewsArticle).filter(models.NewsArticle.id == article_id).first()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article

@app.put("/news/{article_id}", response_model=schemas.NewsArticle)
def update_news_article(
    article_id: int,
    article: schemas.NewsArticleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_article = db.query(models.NewsArticle).filter(models.NewsArticle.id == article_id).first()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this article")
    
    db_article.title = article.title
    db_article.content = article.content
    db.commit()
    db.refresh(db_article)
    return db_article

@app.delete("/news/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin) # Only admins can delete
):
    db_article = db.query(models.NewsArticle).filter(models.NewsArticle.id == article_id).first()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    
    db.delete(db_article)
    db.commit()
    return {"detail": "Article deleted successfully"}

