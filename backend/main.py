import logging
from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from config import CORS_ORIGINS
from database import get_db
from routers import auth, rooms, bookings, admin

app = FastAPI(title='TechnoPark API', version='1.0.0', description='Booking workspace gratis, dua jam per tanggal penggunaan, dalam WIB.')
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=False,
                   allow_methods=['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
                   allow_headers=['Authorization', 'Content-Type'])

@app.middleware('http')
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.exception_handler(RequestValidationError)
async def invalid_input(request, exc):
    # Jangan kirim ulang input, password, atau exception context dari Pydantic.
    errors = [{'field': '.'.join(str(p) for p in e['loc'][1:]), 'message': e['msg']} for e in exc.errors()]
    return JSONResponse(status_code=422, content={'detail': 'Periksa kembali data yang Anda masukkan.', 'errors': errors})

@app.exception_handler(SQLAlchemyError)
async def database_error(request, exc):
    logging.getLogger('uvicorn.error').error('Operasi database gagal: %s', type(exc).__name__)
    return JSONResponse(status_code=503, content={'detail': 'Penyimpanan sementara tidak tersedia. Silakan coba lagi.'})

@app.get('/api/health', tags=['Sistem'], summary='Periksa API dan koneksi MySQL')
def health(db: Session = Depends(get_db)):
    db.execute(text('SELECT 1'))
    return {'status': 'ok', 'database': 'mysql', 'timezone': 'Asia/Jakarta'}

for router in [auth.router, rooms.router, bookings.router, admin.router]:
    app.include_router(router)
