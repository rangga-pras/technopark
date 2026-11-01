import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User
from schemas import RegisterIn, LoginIn, TokenOut, UserOut
from security import (DUMMY_HASH, create_token, current_user, hash_password, limiter, verify_password)

router = APIRouter(prefix='/api/auth', tags=['Akun'])
log = logging.getLogger('uvicorn.error')

@router.post('/register', response_model=UserOut, status_code=201, summary='Daftarkan akun pengguna')
def register(data: RegisterIn, request: Request, db: Session = Depends(get_db)):
    limiter.check(request, 'register', 5)
    user = User(name=data.name, email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Email sudah digunakan. Masuk dengan akun Anda.')
    db.refresh(user)
    return user

@router.post('/login', response_model=TokenOut, summary='Masuk dan terima bearer token')
def login(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    limiter.check(request, 'login', 10)
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    correct = verify_password(data.password, user.password_hash if user else DUMMY_HASH)
    if not user or not correct or not user.is_active:
        log.warning('Login ditolak')
        raise HTTPException(401, 'Email atau kata sandi salah, atau akun tidak aktif.')
    return TokenOut(access_token=create_token(user.id), user=UserOut.model_validate(user))

@router.get('/me', response_model=UserOut, summary='Lihat profil sendiri')
def me(user: User = Depends(current_user)):
    return user
