from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ExternalIndustryIdentifierDTO(BaseModel):
    type: str
    identifier: str


class ExternalImageLinksDTO(BaseModel):
    thumbnail: Optional[HttpUrl] = None


class ExternalVolumeInfoDTO(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    authors: list[str] = Field(default_factory=list)
    publisher: Optional[str] = None
    publishedDate: Optional[str] = None
    description: Optional[str] = None
    industryIdentifiers: list[ExternalIndustryIdentifierDTO] = Field(
        default_factory=list
    )
    pageCount: Optional[int] = None
    averageRating: Optional[float] = None
    ratingsCount: Optional[int] = None
    language: Optional[str] = None
    imageLinks: Optional[ExternalImageLinksDTO] = None
    previewLink: Optional[HttpUrl] = None
    infoLink: Optional[HttpUrl] = None
    canonicalVolumeLink: Optional[HttpUrl] = None


class ExternalBookItemDTO(BaseModel):
    id: str
    volumeInfo: ExternalVolumeInfoDTO


class ExternalBookSearchResponseDTO(BaseModel):
    totalItems: int
    items: list[ExternalBookItemDTO] = Field(default_factory=list)
