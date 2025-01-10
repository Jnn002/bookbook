from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def read_root():
    return {'Hello': 'World'}


@app.get('/greet/{name}')
async def greet(name: str = 'User', age: int | None = None) -> dict:
    return {'message': f'Hello {name.capitalize()}', 'age': age}
