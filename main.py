from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, auth
from database import SessionLocal, engine

# This line creates the database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Authentication Endpoints ---

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.OAuth2PasswordRequestForm, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
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
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user

# --- News Article CRUD Endpoints ---

@app.post("/articles/", response_model=schemas.NewsArticle, status_code=status.HTTP_201_CREATED)
def create_article(article: schemas.NewsArticleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Simple authorization: only admins can create articles
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can create articles")
    db_article = models.NewsArticle(**article.dict(), owner_id=current_user.id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@app.get("/articles/", response_model=list[schemas.NewsArticle])
def read_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = db.query(models.NewsArticle).offset(skip).limit(limit).all()
    return articles

@app.get("/articles/{article_id}", response_model=schemas.NewsArticle)
def read_article(article_id: int, db: Session = Depends(get_db)):
    db_article = db.query(models.NewsArticle).filter(models.NewsArticle.id == article_id).first()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article

@app.put("/articles/{article_id}", response_model=schemas.NewsArticle)
def update_article(article_id: int, article: schemas.NewsArticleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can update articles")
    
    db_article = db.query(models.NewsArticle).filter(models.NewsArticle.id == article_id).first()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
        
    db_article.title = article.title
    db_article.content = article.content
    db.commit()
    db.refresh(db_article)
    return db_article

@app.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can delete articles")
        
    db_article = db.query(models.NewsArticle).filter(models.NewsArticle.id == article_id).first()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
        
    db.delete(db_article)
    db.commit()
    return

