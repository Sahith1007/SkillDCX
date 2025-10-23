# backend/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "supersecretkey"  # change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# fake database
fake_users_db = {
    "university1": {
        "username": "university1",
        "password": pwd_context.hash("password123"),
        "role": "issuer",
    },
    "company1": {
        "username": "company1",
        "password": pwd_context.hash("password123"),
        "role": "verifier",
    },
    "student1": {
        "username": "student1",
        "password": pwd_context.hash("password123"),
        "role": "student",
    },
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires,
    )
    return {"access_token": token, "token_type": "bearer"}
    user = authenticate_user(form_data.username, form_data.password)
