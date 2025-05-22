import uuid
from datetime import date, datetime, timezone
from typing import Optional

from src.application.dtos.external_book_dtos import (
    ExternalBookItemDTO,
    ExternalBookSearchResponseDTO,
)
from src.application.ports.out.book_repository import BookRepository
from src.application.ports.out.cache_port import CachePort
from src.application.ports.out.external_book_service_port import ExternalBookServicePort
from src.application.ports.out.favorite_repository import FavoriteRepository
from src.application.ports.out.review_repository import ReviewRepository
from src.domain.book.book import DomainBook
from src.domain.book.value_objects.book_description import BookDescription
from src.domain.book.value_objects.book_pagecount import BookPageCount
from src.domain.book.value_objects.book_subtitle import BookSubtitle
from src.domain.book.value_objects.book_title import BookTitle


class BookApplicationService:
    def __init__(
        self,
        book_repository: BookRepository,
        external_book_service: ExternalBookServicePort,
        favorite_repository: FavoriteRepository,
        review_repository: ReviewRepository,
        cache: CachePort,
    ):
        self._book_repository = book_repository
        self._external_book_service = external_book_service
        self._favorite_repository = favorite_repository
        self._review_repository = review_repository
        self._cache = cache

    async def _parse_google_published_date(
        self, published_date_str: Optional[str]
    ) -> Optional[date]:
        """
        Parse the Google Books API published date string into a date object.

        :param published_date_str: The published date string from the Google Books API.
        :return: A date object representing the published date, or None if parsing fails.
        """
        if not published_date_str:
            return None

        try:
            if len(published_date_str) == 10:
                return datetime.strptime(published_date_str, '%Y-%m-%d').date()
            if len(published_date_str) == 7:
                dt = datetime.strptime(published_date_str, '%Y-%m').date()
                return date(dt.year, dt.month, 1)
            if len(published_date_str) == 4:
                dt = datetime.strptime(published_date_str, '%Y').date()
                return date(dt.year, 1, 1)
            return None
        except ValueError:
            return None

    async def _map_external_to_domain_book_for_registration(
        self, external_data: ExternalBookItemDTO
    ) -> DomainBook:
        """
        Map external book data to a domain book object for registration.

        :param external_data: The external book data.
        :return: A DomainBook object.
        """
        parsed_published_date = await self._parse_google_published_date(
            external_data.volumeInfo.publishedDate
        )

        db_published_date = (
            parsed_published_date if parsed_published_date else date(1, 1, 1)
        )

        current_time = datetime.now(timezone.utc)

        # TODO: implement ISBN parsing logic
        return DomainBook(
            id=uuid.uuid4(),
            title=BookTitle(external_data.volumeInfo.title),
            subtitle=BookSubtitle(external_data.volumeInfo.subtitle or '-'),
            description=BookDescription(external_data.volumeInfo.description or '-'),
            authors=external_data.volumeInfo.authors,
            publisher=external_data.volumeInfo.publisher or 'N/A',
            published_date=db_published_date,
            page_count=BookPageCount(external_data.volumeInfo.pageCount or 0),
            language=external_data.volumeInfo.language or 'N/A',
            created_at=current_time,
            updated_at=current_time,
            cover_image_url=(
                str(external_data.volumeInfo.imageLinks.thumbnail)
                if external_data.volumeInfo.imageLinks
                and external_data.volumeInfo.imageLinks.thumbnail
                else 'default_cover_image_url'
            ),
            google_book_id=external_data.id,
        )

    async def register_book_from_google_if_not_exists(
        self, google_book_id: str
    ) -> DomainBook:
        """
        Register a book from Google Books API if it doesn't already exist in the database.

        :param google_book_id: The Google Books ID of the book to register.
        :return: The registered DomainBook object.
        """
        existing_book = await self._book_repository.get_book_by_google_id(
            google_book_id
        )
        if existing_book:
            return existing_book

        external_data = (
            await self._external_book_service.get_book_details_by_external_id(
                google_book_id
            )
        )
        if not external_data:
            raise ValueError(
                f'Book with Google ID {google_book_id} not found in external service.'
            )

        domain_book_to_register = (
            await self._map_external_to_domain_book_for_registration(external_data)
        )

        return await self._book_repository.save_book(domain_book_to_register)

    async def search_book_via_external_service(
        self, query: str, page_index: int = 0, page_size: int = 10
    ) -> ExternalBookSearchResponseDTO:
        """Busca libros usando el servicio externo, aplicando caché."""
        cache_key = f'external_search:q={query}:idx={page_index}:size={page_size}'
        cached_response = await self._cache.get(cache_key)
        if cached_response:
            # We assume that we saved the complete DTO in cache and Pydantic can reconstruct it
            # Si guardaste un dict, necesitas: ExternalBookSearchResponseDTO.model_validate(cached_response)
            if isinstance(
                cached_response, ExternalBookSearchResponseDTO
            ):  # O dict y validas
                return cached_response
            elif isinstance(cached_response, dict):
                return ExternalBookSearchResponseDTO.model_validate(cached_response)

        response = await self._external_book_service.search_books(
            query=query, page_index=page_index, page_size=page_size
        )

        await self._cache.set(cache_key, response.model_dump(), expire_seconds=3600)
        return response

    async def get_book_details_for_display(
        self,
        google_book_id: str,
        request_user_id: Optional[uuid.UUID] = None,
    ) -> dict:
        external_data_dto = (
            await self._external_book_service.get_book_details_by_external_id(
                google_book_id
            )
        )
        if not external_data_dto:
            raise ValueError(
                f'Book with Google ID {google_book_id} not found in external service.'
            )

        internal_book_domain = await self.register_book_from_google_if_not_exists(
            google_book_id
        )

        local_reviews_domain = await self._review_repository.get_reviews_by_book_id(
            internal_book_domain.id
        )

        is_favorite_by_user = False
        if request_user_id:
            is_favorite_by_user = (
                await self._favorite_repository.is_book_favorited_by_user(
                    user_id=request_user_id, book_id=internal_book_domain.id
                )
            )

        reviews_for_response = [
            {
                'id': rev.id,
                'rating': rev.rating.value,
                'review_text': rev.review_text.value,
                'user_id': rev.user_id,
                'created_at': rev.created_at.isoformat(),
                'updated_at': rev.updated_at.isoformat(),
            }
            for rev in local_reviews_domain
        ]

        return {
            'internal_system_id': internal_book_domain.id,
            'google_book_id': external_data_dto.id,
            'title': external_data_dto.volumeInfo.title,
            'authors': external_data_dto.volumeInfo.authors,
            'publisher': external_data_dto.volumeInfo.publisher,
            'published_date_str': external_data_dto.volumeInfo.publishedDate,
            'description': external_data_dto.volumeInfo.description,
            'cover_image_url': str(external_data_dto.volumeInfo.imageLinks.thumbnail)
            if external_data_dto.volumeInfo.imageLinks
            and external_data_dto.volumeInfo.imageLinks.thumbnail
            else 'default_cover_image_url',
            'page_count': external_data_dto.volumeInfo.pageCount,
            'language': external_data_dto.volumeInfo.language,
            'local_reviews': reviews_for_response,
            'is_favorited_by_current_user': is_favorite_by_user,
        }

    # TODO: refactor all this methods, check isbn parsing and cover image url implementation
