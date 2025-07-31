import os
from datetime import datetime

import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from typing import Optional

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
    password = Column(String, nullable=True) # Nullable for OAuth users
    email = Column(String, nullable=False, unique=True, index=True)
    pfp_key = Column(String, nullable=True, unique=True) # Key for fetching profile picture stored in S3
    provider = Column(String, nullable=False) # Google, Github, Local
    provider_id = Column(String, nullable=False, unique=True) # ID of 'local' for local users
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)
    last_login_at = Column(DateTime, default=datetime.now(), nullable=False)


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    theme = Column(String, default="light", nullable=False) # Light, Dark, Beige
    safesearch = Column(String, default="moderate", nullable=False) # Off, Moderate, Strict
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)

class UserSearchHistory(Base):
    __tablename__ = "user_search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(String, nullable=False)
    queried_at = Column(DateTime, default=datetime.now(), nullable=False)


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feedback = Column(String, nullable=False)
    submitted_at = Column(DateTime, default=datetime.now(), nullable=False)


class DeveloperResponse(Base):
    __tablename__ = "developer_response"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    response = Column(String, nullable=False)
    submitted_at = Column(DateTime, default=datetime.now(), nullable=False)


class Database:
    def __init__(self):
        self.SessionLocal = SessionLocal
        Base.metadata.create_all(bind=engine)

    # User table
    def create_user(
            self, 
            username: str, 
            email: str,
            provider: str,
            provider_id: str,
            password: Optional[str] = None, 
        ) -> User:

        db = self.SessionLocal()

        try:
            if password:
                password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            db_user = User(
                username=username, 
                password=password,
                email=email, 
                provider=provider, 
                provider_id=provider_id
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            return db_user

        except Exception as e:
            db.rollback()
            return f"Failed to create user ({e})"

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
            return f"Failed to read user ({e})"

        finally:
            db.close()
                
    def update_user(
            self, 
            user_id: int, 
            username: Optional[str] = None, 
            password: Optional[str] = None, 
            email: Optional[str] = None, 
            last_login_at: Optional[datetime] = None,
            pfp_key: Optional[str] = None
        ) -> User:

        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return None
            
            if username:
                db_user.username = username
            if password:
                db_user.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            if email:
                db_user.email = email
            if last_login_at:
                db_user.last_login_at = last_login_at
            if pfp_key:
                db_user.pfp_key = pfp_key # If the user is changing their pfp, call storage.delete_pfp() to remove the old pfp, then get the key returned from upload_pfp and update it here

            db.commit()
            db.refresh(db_user)

            return db_user

        except Exception as e:
            db.rollback()
            return f"Failed to update user ({e})"

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
            return f"Failed to delete user ({e})"

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
            return f"Failed to create user preference ({e})"
        
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
            return f"Failed to read user preference ({e})"

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

            return db_user_preference

        except Exception as e:
            db.rollback()
            return f"Failed to update user preference ({e})"

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
            return f"Failed to delete user preference ({e})"

        finally:
            db.close()


    # Authentication (Local accounts only; Google and GitHub accounts are handled by OAuth)
    def check_login_credentials(self, username_or_email: str, password: str) -> bool:
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
            return f"Failed to check login credentials ({e})"

        finally:
            db.close()

    def login_after_successful_2fa(self, username_or_email: str) -> User:
        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.username == username_or_email).first()

            if not db_user:
                db_user = db.query(User).filter(User.email == username_or_email).first()

            db_user.last_login_at = datetime.now()

            db.commit()
            db.refresh(db_user)

            return db_user

        except Exception as e:
            db.rollback()
            return f"Failed to login after successful 2FA ({e})"

        finally:
            db.close()

    # UserSearchHistory table
    def log_user_search(self, user_id: int, query: str) -> UserSearchHistory:
        db = self.SessionLocal()

        try:
            db_user_search_history = UserSearchHistory(user_id=user_id, query=query)

            db.add(db_user_search_history)
            db.commit()
            db.refresh(db_user_search_history)

            return db_user_search_history
        
        except Exception as e:
            db.rollback()
            return f"Failed to log search query ({e})"
        
        finally:
            db.close()
    
    def read_user_search_history(self, user_id: int) -> UserSearchHistory:
        db = self.SessionLocal()

        try:
            db_user_search_history = db.query(UserSearchHistory).filter(UserSearchHistory.user_id == user_id).all()

            if not db_user_search_history:
                return None

            return db_user_search_history
        
        except Exception as e:
            return f"Failed to read user search history ({e})"
        
        finally:
            db.close()

    # UserFeedback table
    def log_user_feedback(self, user_id: int, feedback: str) -> UserFeedback:
        db = self.SessionLocal()

        try:
            db_user_feedback = UserFeedback(user_id=user_id, feedback=feedback)

            db.add(db_user_feedback)
            db.commit()
            db.refresh(db_user_feedback)

            return db_user_feedback
        
        except Exception as e:
            db.rollback()
            return f"Failed to log user feedback ({e})"
        
        finally:
            db.close()
    
    def read_user_feedback(self, user_id: int) -> UserFeedback:
        db = self.SessionLocal()

        try:
            db_user_feedback = db.query(UserFeedback).filter(UserFeedback.user_id == user_id).all()

            if not db_user_feedback:
                return None

            return db_user_feedback
        
        except Exception as e:
            return f"Failed to read user feedback ({e})"
        
        finally:
            db.close()

    # DeveloperResponse table
    def log_developer_response(self, user_id: int, response: str) -> DeveloperResponse:
        db = self.SessionLocal()

        try:
            db_developer_response = DeveloperResponse(user_id=user_id, response=response)

            db.add(db_developer_response)
            db.commit()
            db.refresh(db_developer_response)

            return db_developer_response
        
        except Exception as e:
            db.rollback()
            return f"Failed to log developer response ({e})"
        
        finally:
            db.close()  
    
    def read_developer_response(self, user_id: int) -> DeveloperResponse:
        db = self.SessionLocal()

        try:
            db_developer_response = db.query(DeveloperResponse).filter(DeveloperResponse.user_id == user_id).all()

            if not db_developer_response:
                return None

            return db_developer_response
        
        except Exception as e:
            return f"Failed to read developer response ({e})"
        
        finally:
            db.close()

db = Database()
