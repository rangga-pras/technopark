from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import database_url

class Base(DeclarativeBase):
    pass

engine = create_engine(database_url(), pool_pre_ping=True, pool_recycle=1800,
                       connect_args={'connect_timeout': 5}, hide_parameters=True)
SessionLocal = sessionmaker(engine, autoflush=False, expire_on_commit=False)

def get_db():
    with SessionLocal() as db:
        yield db
