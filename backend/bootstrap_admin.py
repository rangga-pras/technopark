from getpass import getpass
from sqlalchemy import select
from database import SessionLocal
from models import User
from schemas import RegisterIn
from security import hash_password

def main():
    data = RegisterIn(name=input('Nama admin: '), email=input('Email admin: '),
                      password=getpass('Kata sandi: '), confirm_password=getpass('Ulangi kata sandi: '))
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == data.email)):
            raise SystemExit('Email sudah digunakan. Gunakan pengelolaan akun oleh admin.')
        db.add(User(name=data.name, email=data.email, role='admin', password_hash=hash_password(data.password)))
        db.commit()
    print('Admin berhasil dibuat; kata sandi tidak disimpan dalam source atau log.')

if __name__ == '__main__':
    main()
