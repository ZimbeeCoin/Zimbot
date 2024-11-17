class MissingSecretError(Exception):
    """
    Custom exception for handling missing critical secrets.

    Attributes:
        secret_key (str): The key of the missing secret.
        message (str): The error message describing the missing secret.
    """

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.message = f"Missing critical secret: '{secret_key}'"
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
