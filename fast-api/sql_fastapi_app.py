from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# Database Configuration
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:example@localhost/socialmedia"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for ORM models
Base = declarative_base()

# ORM model for the Users table
class UserModel(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic model for user data
class User(BaseModel):
    username: str
    email: str

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE
@app.post("/users")
def create_user(user: User, db: Session = Depends(get_db)):
    db_user = UserModel(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# READ
@app.get("/users")
def read_users(skip: int = 0, db: Session = Depends(get_db)):
    users = db.query(UserModel).offset(skip).all()
    return users

# UPDATE
@app.put("/users/{user_id}")
def update_user(user_id: int, user: User, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user

# DELETE
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return db_user

@app.get("/")
def read_root():
    return {"Application details": "fasi-api sql application"}
