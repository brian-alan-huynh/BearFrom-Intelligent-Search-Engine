import os
from datetime import datetime

import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from typing import Optional
from fastapi import HTTPException

load_dotenv()
env = os.getenv

DATABASE_URL = f"postgresql+psycopg2://{env('RDS_USER')}:{env('RDS_PASS')}@{env('RDS_HOST')}:{env('RDS_PORT')}/{env('RDS_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)
    last_login_at = Column(DateTime, default=datetime.now(), nullable=False)
    pfp_key = Column(String, nullable=True, unique=True) # For fetching profile picture from S3


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    theme = Column(String, default="light", nullable=False) # Light, Dark, Beige
    safesearch = Column(String, default="moderate", nullable=False) # Off, Moderate, Strict


class Database:
    def __init__(self):
        self.SessionLocal = SessionLocal
        Base.metadata.create_all(bind=engine)

    # User table
    def create_user(
            self, 
            username: str, 
            password: str, 
            email: str
        ) -> User:

        db = self.SessionLocal()

        try:
            password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            db_user = User(username=username, password=password, email=email)

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            return db_user

        except Exception as e:
            db.rollback()
            raise e

        finally:
            db.close()

    def read_user(self, user_id: int) -> User:
        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return None

            return db_user

        except Exception as e:
            raise e

        finally:
            db.close()
                
    def update_user(
            self, 
            user_id: int, 
            username: Optional[str] = None, 
            password: Optional[str] = None, 
            email: Optional[str] = None, 
            updated_at: Optional[datetime] = None,
            last_login_at: Optional[datetime] = None,
            pfp_key: Optional[str] = None
        ) -> User:

        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return None
            
            if updated_at:
                db_user.updated_at = updated_at
            
            else:
                if username:
                    db_user.username = username
                if password:
                    db_user.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                if email:
                    db_user.email = email
                if last_login_at:
                    db_user.last_login_at = last_login_at
                if pfp_key:
                    db_user.pfp_key = pfp_key
                
                db_user.updated_at = datetime.now()

            db.commit()
            db.refresh(db_user)

            return db_user

        except Exception as e:
            db.rollback()
            raise e

        finally:
            db.close()

    def delete_user(self, user_id: int) -> bool:
        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return False

            db.delete(db_user)
            db.commit()

            return True

        except Exception as e:
            db.rollback()
            raise e

        finally:
            db.close()


    # UserPreferences table
    def create_user_preference(self, user_id: int) -> UserPreferences:
        db = self.SessionLocal()

        try:
            db_user_preference = UserPreferences(user_id=user_id)

            db.add(db_user_preference)
            db.commit()
            db.refresh(db_user_preference)

            return db_user_preference
        
        except Exception as e:
            db.rollback()
            raise e
        
        finally:
            db.close()

    def read_user_preference(self, user_id: int) -> UserPreferences:
        db = self.SessionLocal()

        try:
            db_user_preference = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()

            if not db_user_preference:
                return None

            return db_user_preference
        
        except Exception as e:
            raise e

        finally:
            db.close()

    def update_user_preference(
            self, 
            user_id: int, 
            theme: Optional[str] = None, 
            safesearch: Optional[str] = None
        ) -> UserPreferences:

        db = self.SessionLocal()

        try:
            db_user_preference = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
            
            if not db_user_preference:
                return None

            if theme:
                db_user_preference.theme = theme
            if safesearch:
                db_user_preference.safesearch = safesearch
            
            db.commit()
            db.refresh(db_user_preference)
            
            self.update_user(user_id=user_id, updated_at=datetime.now())

            return db_user_preference

        except Exception as e:
            db.rollback()
            raise e

        finally:
            db.close()
    
    def delete_user_preference(self, user_id: int) -> bool:
        db = self.SessionLocal()

        try:
            db_user_preference = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()

            if not db_user_preference:
                return False

            db.delete(db_user_preference)
            db.commit()

            return True

        except Exception as e:
            db.rollback()
            raise e

        finally:
            db.close()


    # Authentication
    def login_user_before_successful_2fa(self, username_or_email: str, password: str) -> bool:
        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.username == username_or_email).first()

            if not db_user:
                db_user = db.query(User).filter(User.email == username_or_email).first()

            if not db_user:
                return False

            if not bcrypt.checkpw(password.encode("utf-8"), db_user.password.encode("utf-8")):
                return False

            return True

        except Exception as e:
            raise e

        finally:
            db.close()

    def login_user_after_successful_2fa(self, username_or_email: str) -> User:
        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.username == username_or_email).first()

            if not db_user:
                db_user = db.query(User).filter(User.email == username_or_email).first()

            db_user.last_login_at = datetime.now()
            db_user.updated_at = datetime.now()

            db.commit()
            db.refresh(db_user)

            return db_user

        except Exception as e:
            raise e

        finally:
            db.close()

db = Database()
