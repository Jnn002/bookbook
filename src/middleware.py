import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request

logger = logging.getLogger('uvicorn.access')
logger.disabled = True


def register_middleware(app: FastAPI):
    @app.middleware('http')
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        processing_time = time.time() - start_time

        client_host = getattr(request.client, 'host', 'unknown')
        client_port = getattr(request.client, 'port', 'unknown')
        message = f'{client_host}:{client_port} - {request.method} - {request.url.path} - {response.status_code} \ncompleted after {processing_time}s'

        print(f'{message}')

        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_headers=['*'],
        allow_methods=['*'],
        allow_credentials=True,
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['localhost', '127.0.0.1'])
