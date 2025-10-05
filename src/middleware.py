import logging
import time
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = logging.getLogger('uvicorn.access')
logger.disabled = True


def register_middleware(app: FastAPI) -> None:
    """Register all middleware for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.middleware('http')
    async def custom_logging(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Log request processing time and details.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler in the chain.

        Returns:
            The HTTP response with an added X-Process-Time header.
        """
        start_time = time.perf_counter()

        response = await call_next(request)
        processing_time = time.perf_counter() - start_time

        client_host = getattr(request.client, 'host', 'unknown')
        client_port = getattr(request.client, 'port', 'unknown')
        message = (
            f'{client_host}:{client_port} - {request.method} - '
            f'{request.url.path} - {response.status_code} '
            f'completed after {processing_time:.4f}s'
        )

        print(message)

        # Add processing time to response headers as per FastAPI best practices
        response.headers['X-Process-Time'] = str(processing_time)

        return response

    # CORS middleware - consider restricting origins in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],  # TODO: Replace with specific origins in production
        allow_headers=['*'],
        allow_methods=['*'],
        allow_credentials=True,  # Consider setting to False if using allow_origins=['*']
    )

    # Trusted Host middleware for additional security
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['localhost', '127.0.0.1'])
