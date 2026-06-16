from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import secrets
import hashlib

from ..core.config import settings
from ..db.base import get_db
from ..db.models import User
from pydantic import BaseModel, EmailStr

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== SCHEMAS ====================
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class MessageResponse(BaseModel):
    message: str

# ==================== HELPERS ====================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def generate_verification_token(email: str) -> str:
    token = secrets.token_urlsafe(32)
    return token

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

verification_tokens = {}

# ==================== ROUTES ====================

@router.post("/register", response_model=Token)
async def register(
    user: UserCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    verification_token = generate_verification_token(user.email)
    token_hash = hash_token(verification_token)
    
    verification_tokens[token_hash] = {
        "email": user.email,
        "expires": datetime.utcnow() + timedelta(hours=24)
    }

    verification_link = f"http://localhost:8000/auth/verify-email?token={verification_token}"
    print(f"\n=== VERIFICATION EMAIL ===")
    print(f"To: {user.email}")
    print(f"Click to verify: {verification_link}")
    print(f"==========================\n")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not getattr(db_user, 'is_verified', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in. Check your inbox.",
        )

    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    token_hash = hash_token(token)
    
    if token_hash not in verification_tokens:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    token_data = verification_tokens[token_hash]
    
    if datetime.utcnow() > token_data["expires"]:
        del verification_tokens[token_hash]
        raise HTTPException(status_code=400, detail="Verification token has expired")
    
    user = db.query(User).filter(User.email == token_data["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = True
    db.commit()
    
    del verification_tokens[token_hash]
    
    return {"message": "Email verified successfully! You can now log in."}


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if getattr(user, 'is_verified', False):
        return {"message": "Email is already verified."}

    verification_token = generate_verification_token(email)
    token_hash = hash_token(verification_token)
    
    verification_tokens[token_hash] = {
        "email": email,
        "expires": datetime.utcnow() + timedelta(hours=24)
    }

    verification_link = f"http://localhost:8000/auth/verify-email?token={verification_token}"
    print(f"\n=== RESENT VERIFICATION EMAIL ===")
    print(f"To: {email}")
    print(f"Click to verify: {verification_link}")
    print(f"==================================\n")

    return {"message": "Verification email has been resent. Please check your inbox."}
