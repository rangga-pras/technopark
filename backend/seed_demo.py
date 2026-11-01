"""Buat ulang akun demo untuk evaluasi lokal; tidak boleh dijalankan di production."""

from sqlalchemy import select

from config import APP_ENV
from database import SessionLocal
from models import User
from security import hash_password


DEMO_USERS = (
    {
        "name": "Admin Demo",
        "email": "admin@technopark.id",
        "password": "AdminTechno#2026",
        "role": "admin",
    },
    {
        "name": "User Demo",
        "email": "user@technopark.id",
        "password": "UserTechno#2026",
        "role": "user",
    },
)


def seed_demo_users():
    if APP_ENV.lower() == "production":
        raise SystemExit("Akun demo tidak boleh dibuat pada environment production.")

    with SessionLocal() as db:
        for data in DEMO_USERS:
            user = db.scalar(select(User).where(User.email == data["email"]))
            if user is None:
                user = User(email=data["email"])
                db.add(user)

            user.name = data["name"]
            user.password_hash = hash_password(data["password"])
            user.role = data["role"]
            user.is_active = True

        db.commit()


if __name__ == "__main__":
    seed_demo_users()
    print("Akun demo lokal siap: 1 admin dan 1 user aktif.")
