import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import database_connect_args, database_url

class Base(DeclarativeBase):
    pass

engine_options = {
    'pool_pre_ping': True,
    'pool_recycle': 300 if os.getenv('VERCEL') else 1800,
    'connect_args': database_connect_args(),
    'hide_parameters': True,
}
if os.getenv('VERCEL'):
    # Batasi koneksi per instance Function agar tier kecil Aiven tidak kehabisan koneksi.
    engine_options.update(pool_size=1, max_overflow=1, pool_timeout=10)

engine = create_engine(database_url(), **engine_options)
SessionLocal = sessionmaker(engine, autoflush=False, expire_on_commit=False)

def get_db():
    with SessionLocal() as db:
        yield db
