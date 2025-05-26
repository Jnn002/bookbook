from abc import ABC, abstractmethod


class PasswordSecurityPort(ABC):
    """
    Interface for password-related operations.
    """

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """
        Hashes the given password.

        :param data: The password to hash.
        :return: The hashed password.
        """
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies the given plain password against the hashed password.

        :param plain_password: The plain password to verify.
        :param hashed_password: The hashed password to verify against.
        :return: True if the passwords match, False otherwise.
        """
        pass
