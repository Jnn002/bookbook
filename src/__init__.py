from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.books.routes import book_router
from src.db.main import init_db


@asynccontextmanager
async def life_span(app: FastAPI):
    print('starting app')
    await init_db()
    yield
    print('stopping app')


version = '0.2.0'

app = FastAPI(version=version, lifespan=life_span)

app.include_router(book_router, prefix=f'/api/{version}/books', tags=['books'])
