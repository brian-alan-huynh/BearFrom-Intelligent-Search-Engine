# Core and Server
import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union

# FastAPI
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status, Header, Cookie, Query, Body, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# CSRF Protection
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Authentication & Security
import bcrypt
import pyotp
from authlib.integrations.starlette_client import OAuth
from authlib.oauth2 import OAuth2Error
from jose import JWTError, jwt



# Data Validation
from pydantic import BaseModel, EmailStr, validator, Field
from pydantic_settings import BaseSettings

# Environment Variables
from dotenv import load_dotenv
load_dotenv()


