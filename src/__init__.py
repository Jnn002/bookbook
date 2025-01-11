from fastapi import FastAPI

from src.books.routes import book_router

version = '0.1.0'

app = FastAPI(version=version)

app.include_router(book_router, prefix=f'/api/{version}/books', tags=['books'])
