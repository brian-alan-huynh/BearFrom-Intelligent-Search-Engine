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
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True) # Nullable for OAuth users
    email = Column(String, nullable=False, unique=True, index=True)
    s3_pfp_url = Column(String, nullable=True, unique=True) # Key for fetching profile picture stored in S3
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

class Database:
    def __init__(self):
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

    # User table
    def create_user(
            self, 
            username: str, 
            email: str,
            provider: str,
            provider_id: str,
            password: Optional[str] = None, 
        ) -> dict[str, bool | int | str]:

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

            return {
                "success": True,
                "response": db_user.id,
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "response": f"Failed to create user ({e})",
            }

        finally:
            db.close()

    def read_user(self, user_id: int) -> dict[str, bool | str | User]:
        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return {
                    "success": False,
                    "response": "User not found",
                }

            return {
                "success": True,
                "response": {
                    "username": db_user.username,
                    "email": db_user.email,
                    "s3_pfp_url": db_user.s3_pfp_url,
                    "provider": db_user.provider,
                    "provider_id": db_user.provider_id,
                    "created_at": str(db_user.created_at),
                    "updated_at": str(db_user.updated_at),
                    "last_login_at": str(db_user.last_login_at),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to read user ({e})",
            }

        finally:
            db.close()
                
    def update_user(
            self, 
            user_id: int, 
            username: Optional[str] = None, 
            password: Optional[str] = None, 
            email: Optional[str] = None, 
            last_login_at: Optional[datetime] = None,
            s3_pfp_url: Optional[str] = None
        ) -> dict[str, bool | str]:

        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return {
                    "success": False,
                    "response": "User not found",
                }
            
            if username:
                db_user.username = username
            if password:
                db_user.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            if email:
                db_user.email = email
            if last_login_at:
                db_user.last_login_at = last_login_at
            if s3_pfp_url:
                db_user.s3_pfp_url = s3_pfp_url # If the user is changing their pfp, call storage.delete_pfp() to remove the old pfp, then get the key returned from upload_pfp and update it here

            db.commit()
            db.refresh(db_user)
            
            return {
                "success": True,
                "response": "User updated successfully",
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "response": f"Failed to update user ({e})",
            }

        finally:
            db.close()

    def delete_user(self, user_id: int) -> dict[str, bool | str]:
        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return {
                    "success": False,
                    "response": "User not found",
                }

            db.delete(db_user)
            db.commit()

            return {
                "success": True,
                "response": "User deleted successfully",
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "response": f"Failed to delete user ({e})",
            }

        finally:
            db.close()


    # UserPreferences table
    def create_user_preference(self, user_id: int) -> dict[str, bool | str]:
        db = self.SessionLocal()

        try:
            db_user_preference = UserPreferences(user_id=user_id)

            db.add(db_user_preference)
            db.commit()
            db.refresh(db_user_preference)

            return {
                "success": True,
                "response": "", # To be used internally; does not interact with the user
            }
        
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "response": "",
            }
        
        finally:
            db.close()

    def read_user_preference(self, user_id: int) -> dict[str, bool | dict[str, str]]:
        db = self.SessionLocal()

        try:
            db_user_preference = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()

            if not db_user_preference:
                return {
                    "success": False,
                    "response": "User preference not found",
                }

            return {
                "success": True,
                "response": {
                    "theme": db_user_preference.theme,
                    "safesearch": db_user_preference.safesearch,
                    "updated_at": str(db_user_preference.updated_at),
                },
            }
        
        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to read user preference ({e})",
            }

        finally:
            db.close()

    def update_user_preference(
            self, 
            user_id: int, 
            theme: Optional[str] = None, 
            safesearch: Optional[str] = None
        ) -> dict[str, bool | str]:

        db = self.SessionLocal()

        try:
            db_user_preference = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
            
            if not db_user_preference:
                return {
                    "success": False,
                    "response": "User preference not found",
                }

            if theme:
                db_user_preference.theme = theme
            if safesearch:
                db_user_preference.safesearch = safesearch
            
            db.commit()
            db.refresh(db_user_preference)

            return {
                "success": True,
                "response": "User preference updated successfully",
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "response": f"Failed to update user preference ({e})",
            }

        finally:
            db.close()

    # Authentication (Local accounts only; Google and GitHub accounts are handled by OAuth)
    def check_login_credentials(self, username_or_email: str, password: str) -> dict[str, bool | str]:
        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.username == username_or_email).first()

            if not db_user:
                db_user = db.query(User).filter(User.email == username_or_email).first()

            if not db_user:
                return {
                    "success": False,
                    "response": "User not found",
                }

            if not bcrypt.checkpw(password.encode("utf-8"), db_user.password.encode("utf-8")):
                return {
                    "success": False,
                    "response": "Incorrect password",
                }

            return {
                "success": True,
                "response": "Credentials are correct",
            }

        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to check login credentials ({e})",
            }

        finally:
            db.close()

    def login_after_successful_2fa(self, username_or_email: str) -> dict[str, bool | int]:
        db = self.SessionLocal()

        try:
            db_user = db.query(User).filter(User.username == username_or_email).first()

            if not db_user:
                db_user = db.query(User).filter(User.email == username_or_email).first()

            db_user.last_login_at = datetime.now()

            db.commit()
            db.refresh(db_user)

            return {
                "success": True,
                "response": db_user.id,
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "response": f"Failed to login after successful 2FA ({e})",
            }

        finally:
            db.close()

    # UserSearchHistory table
    def log_user_search(self, user_id: int, query: str) -> dict[str, bool | str]:
        db = self.SessionLocal()

        try:
            db_user_search_history = UserSearchHistory(user_id=user_id, query=query)

            db.add(db_user_search_history)
            db.commit()
            db.refresh(db_user_search_history)

            return {
                "success": True,
                "response": "",
            }
        
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "response": f"Failed to log search query ({e})",
            }
        
        finally:
            db.close()
    
    def read_user_search_history(self, user_id: int) -> dict[str, bool | list[dict[str, str]]]:
        db = self.SessionLocal()

        try:
            db_user_search_history = db.query(UserSearchHistory).filter(UserSearchHistory.user_id == user_id).all()

            if not db_user_search_history:
                return {
                    "success": False,
                    "response": "User search history not found",
                }

            return {
                "success": True,
                "response": [
                    { "query": query_record.query, "queried_at": str(query_record.queried_at) }
                    for query_record in db_user_search_history
                ],
            }
        
        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to read user search history ({e})",
            }
        
        finally:
            db.close()

    def delete_user_search_history(self, user_id: int) -> dict[str, bool | str]:
        db = self.SessionLocal()

        try:
            db_user_search_history = db.query(UserSearchHistory).filter(UserSearchHistory.user_id == user_id).all()

            if not db_user_search_history:
                return {
                    "success": False,
                    "response": "User search history not found",
                }

            db.delete(db_user_search_history)
            db.commit()

            return {
                "success": True,
                "response": "User search history deleted successfully",
            }
        
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "response": f"Failed to delete user search history ({e})",
            }
        
        finally:
            db.close()
