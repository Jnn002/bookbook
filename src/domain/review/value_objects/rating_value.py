from dataclasses import dataclass

from src.domain.exceptions.review_exception import (
    InvalidRating,
)


@dataclass(frozen=True)
class RatingVO:
    """
    Value Object representing the rating of a review.
    Ensures the rating is an integer between 1 and 5.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate that the rating is between 1 and 5."""
        if not isinstance(self.value, int) or not (1 <= self.value <= 5):
            raise InvalidRating('Rating must be an integer between 1 and 5')

    def __int__(self) -> int:
        return self.value
