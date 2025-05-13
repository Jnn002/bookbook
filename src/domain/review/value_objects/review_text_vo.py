from dataclasses import dataclass

from src.domain.exceptions.review_exception import (
    EmptyReview,
    LengthExceeded,
)


@dataclass(frozen=True)
class ReviewTextVO:
    """
    Value Object representing the text content of a review.
    Ensures the text is not empty and does not exceed a defined maximum length.
    """

    value: str
    MAX_LENGTH: int = 500

    def __post_init__(self) -> None:
        """Validate the review text."""
        if not isinstance(self.value, str) or not self.value.strip():
            raise EmptyReview('Review text cannot be empty')
        if len(self.value) > self.MAX_LENGTH:
            raise LengthExceeded(
                f'Review text cannot exceed {self.MAX_LENGTH} characters'
            )

    def __str__(self) -> str:
        return self.value
