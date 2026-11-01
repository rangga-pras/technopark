from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from time import monotonic
import secrets
import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config import JWT_SECRET_KEY, TOKEN_MINUTES
from database import get_db
from models import User

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False

DUMMY_HASH = hash_password(secrets.token_urlsafe(24))

def create_token(user_id):
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': str(user_id), 'iat': now, 'exp': now + timedelta(minutes=TOKEN_MINUTES)}, JWT_SECRET_KEY, algorithm='HS256')

bearer = HTTPBearer(auto_error=False)

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    user = None
    if credentials:
        try:
            payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=['HS256'], options={'require': ['sub', 'iat', 'exp']})
            user = db.get(User, int(payload['sub']))
        except (jwt.InvalidTokenError, ValueError, TypeError):
            pass
    if not user or not user.is_active:
        raise HTTPException(401, 'Sesi berakhir atau belum masuk. Silakan masuk kembali.', headers={'WWW-Authenticate': 'Bearer'})
    return user

def require_admin(user: User = Depends(current_user)):
    if user.role != 'admin':
        raise HTTPException(403, 'Akses ini hanya tersedia untuk admin.')
    return user

class RateLimiter:
    """Batas per IP pada satu worker; tidak mempercayai header forwarded dari client."""
    def __init__(self):
        self.hits = defaultdict(deque)
        self.lock = Lock()

    def check(self, request: Request, action: str, limit: int):
        now = monotonic()
        key = (request.client.host if request.client else 'unknown', action)
        with self.lock:
            # Hapus bucket kedaluwarsa supaya alamat baru tidak menumpuk selamanya.
            for old in list(self.hits):
                if not self.hits[old] or self.hits[old][-1] <= now - 60:
                    del self.hits[old]
            bucket = self.hits[key]
            while bucket and bucket[0] <= now - 60:
                bucket.popleft()
            if len(bucket) >= limit:
                raise HTTPException(429, 'Terlalu banyak percobaan. Coba lagi dalam satu menit.', headers={'Retry-After': '60'})
            bucket.append(now)

limiter = RateLimiter()
