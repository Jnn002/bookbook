from abc import ABC, abstractmethod
from typing import Any, Optional


class CachePort(ABC):
    """
    Port defining generic operations for a caching mechanism (e.g., Redis).
    Values are typically serialized (e.g., to JSON strings) before being stored
    and deserialized after retrieval by the cache adapter implementation.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieves an item from the cache by key.
        Returns the deserialized item if found and not expired, otherwise None.
        """
        pass

    @abstractmethod
    async def set(
        self, key: str, value: Any, expire_seconds: Optional[int] = None
    ) -> None:
        """
        Sets an item in the cache. The adapter will handle serialization.
        'expire_seconds': Time in seconds until the item expires.
        If None, uses default TTL or no expiry, depending on cache implementation.
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Deletes an item from the cache by key.
        Returns True if an item was present and deleted, False otherwise.
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Checks if a key exists in the cache."""
        pass

    # TODO: check this methods later
    # @abstractmethod
    # async def increment(self, key: str, amount: int = 1) -> Optional[int]:
    #     """Increments a numerical value stored in the cache."""
    #     pass

    # @abstractmethod
    # async def add_to_set(self, key: str, *values: Any) -> None:
    #     """Adds one or more members to a set stored at key."""
    #     pass
