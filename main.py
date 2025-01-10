from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

app = FastAPI()

books = [
    {
        'id': 1,
        'title': 'Think and Grow Rich',
        'author': 'Napoleon Hill',
        'publisher': 'Random House',
        'published_date': '1937-02-20',
        'page_count': 100,
        'language': 'English',
    },
    {
        'id': 2,
        'title': 'The Great Gatsby',
        'author': 'F. Scott Fitzgerald',
        'publisher': "Charles Scribner's Sons",
        'published_date': '1925-04-10',
        'page_count': 218,
        'language': 'English',
    },
    {
        'id': 3,
        'title': 'To Kill a Mockingbird',
        'author': 'Harper Lee',
        'publisher': 'J.B. Lippincott & Co.',
        'published_date': '1960-07-11',
        'page_count': 281,
        'language': 'English',
    },
    {
        'id': 4,
        'title': '1984',
        'author': 'George Orwell',
        'publisher': 'Secker & Warburg',
        'published_date': '1949-06-08',
        'page_count': 328,
        'language': 'English',
    },
    {
        'id': 5,
        'title': 'Moby-Dick',
        'author': 'Herman Melville',
        'publisher': 'Harper & Brothers',
        'published_date': '1851-10-18',
        'page_count': 635,
        'language': 'English',
    },
    {
        'id': 6,
        'title': 'War and Peace',
        'author': 'Leo Tolstoy',
        'publisher': 'The Russian Messenger',
        'published_date': '1869-01-01',
        'page_count': 1225,
        'language': 'Russian',
    },
    {
        'id': 7,
        'title': 'Pride and Prejudice',
        'author': 'Jane Austen',
        'publisher': 'T. Egerton',
        'published_date': '1813-01-28',
        'page_count': 279,
        'language': 'English',
    },
    {
        'id': 8,
        'title': 'The Catcher in the Rye',
        'author': 'J.D. Salinger',
        'publisher': 'Little, Brown and Company',
        'published_date': '1951-07-16',
        'page_count': 214,
        'language': 'English',
    },
    {
        'id': 9,
        'title': 'The Hobbit',
        'author': 'J.R.R. Tolkien',
        'publisher': 'George Allen & Unwin',
        'published_date': '1937-09-21',
        'page_count': 310,
        'language': 'English',
    },
    {
        'id': 10,
        'title': 'Crime and Punishment',
        'author': 'Fyodor Dostoevsky',
        'publisher': 'The Russian Messenger',
        'published_date': '1866-01-01',
        'page_count': 430,
        'language': 'Russian',
    },
    {
        'id': 11,
        'title': 'The Brothers Karamazov',
        'author': 'Fyodor Dostoevsky',
        'publisher': 'The Russian Messenger',
        'published_date': '1880-01-01',
        'page_count': 824,
        'language': 'Russian',
    },
]


class Book(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str


@app.get('/books', response_model=list[Book])
async def get_all_books():
    return books


@app.post('/books', status_code=status.HTTP_201_CREATED)
async def create_book(book_data: Book) -> dict:
    new_book = book_data.model_dump()
    books.append(new_book)
    return new_book


@app.get('/books/{book_id}')
async def get_book(book_id: int) -> dict:
    for book in books:
        if book['id'] == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')


@app.patch('/books/{book_id}')
async def updata_book(book_id: int, book_update_data: BookUpdateModel) -> dict:
    for book in books:
        if book['id'] == book_id:
            book['title'] = book_update_data.title
            book['author'] = book_update_data.author
            book['publisher'] = book_update_data.publisher
            book['page_count'] = book_update_data.page_count
            book['language'] = book_update_data.language

            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')


@app.delete('/books/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book['id'] == book_id:
            books.remove(book)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')
