from typing import Annotated

from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()


@app.get('/')
async def read_root():
    return {'Hello': 'World'}


@app.get('/greet/{name}')
async def greet(name: str = 'User', age: int | None = None) -> dict:
    return {'message': f'Hello {name.capitalize()}', 'age': age}


class BookCreateModel(BaseModel):
    title: str
    author: str


@app.post('/create_book')
async def create_book(book_data: BookCreateModel) -> dict:
    return {'title': book_data.title, 'author': book_data.author}


@app.get('/get_headers')
async def get_headers(
    accept: Annotated[str | None, Header()] = None,
    content_type: Annotated[str | None, Header()] = None,
    user_agent: Annotated[str | None, Header()] = None,
    host: Annotated[str | None, Header()] = None,
):
    request_headers = {}
    request_headers['Accept'] = accept
    request_headers['Content-Type'] = content_type
    request_headers['User-Agent'] = user_agent
    request_headers['Host'] = host
    return request_headers
