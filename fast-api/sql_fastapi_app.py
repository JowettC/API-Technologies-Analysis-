from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship, joinedload
from pydantic import BaseModel

# Database Configuration
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:example@localhost/socialmedia"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ORM models
class UserModel(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    posts = relationship("PostModel", back_populates="user")
    comments = relationship("CommentModel", back_populates="user")
    likes = relationship("LikeModel", back_populates="user")

class PostModel(Base):
    __tablename__ = "posts"
    post_id = Column(Integer, primary_key=True, index=True)
    content = Column(String(500), index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    comments = relationship("CommentModel", back_populates="post")
    likes = relationship("LikeModel", back_populates="post")
    user = relationship("UserModel", back_populates="posts")

class CommentModel(Base):
    __tablename__ = "comments"
    comment_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    comment_text = Column(String(500), index=True)
    user = relationship("UserModel", back_populates="comments")
    post = relationship("PostModel", back_populates="comments")

class LikeModel(Base):
    __tablename__ = "likes"
    like_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("UserModel", back_populates="likes")
    post = relationship("PostModel", back_populates="likes")

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: str

class PostBase(BaseModel):
    content: str

class CommentBase(BaseModel):
    comment_text: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True

class LikeBase(BaseModel):
    pass

class PostCreate(PostBase):
    pass

class Post(PostBase):
    post_id: int
    user_id: int
    user: UserBase

    class Config:
        orm_mode = True



class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    comment_id: int
    post_id: int
    user_id: int

    class Config:
        orm_mode = True


class LikeCreate(LikeBase):
    pass

class Like(LikeBase):
    like_id: int
    post_id: int
    user_id: int

    class Config:
        orm_mode = True

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI routes
@app.post("/users", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserModel(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users", response_model=List[User])
def read_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.email = user.email
    db.commit()
    return db_user

@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return db_user



@app.get("/users/posts")
def read_user_posts(db: Session = Depends(get_db)):
    posts = db.query(PostModel).options(joinedload(PostModel.user)).all()
    return posts

@app.get("/users/comments")
def read_user_comments(db: Session = Depends(get_db)):
    comments = db.query(CommentModel).options(joinedload(CommentModel.user)).all()
    return comments

@app.get("/posts/likes")
def read_post_likes(db: Session = Depends(get_db)):
    posts = db.query(PostModel).options(joinedload(PostModel.likes)).all()
    return posts

@app.get("/posts/likes/users")
def read_post_likes_users(db: Session = Depends(get_db)):
    # include post, user and likes
    posts = db.query(PostModel).options(joinedload(PostModel.likes).joinedload(LikeModel.user)).all()
    return posts

# choose port 8000
# uvicorn sql_fastapi_app:app --reload --port 8000