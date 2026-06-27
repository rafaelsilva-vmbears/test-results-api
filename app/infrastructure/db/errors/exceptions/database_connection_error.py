""" Database connection error. """


class CloseDatabaseConnectionError(Exception):
    """Exception raised for errors in database connection operations."""

    def __init__(self, message: str = "Error closing database connection"):
        self.message = message
        super().__init__(self.message)


class DatabaseConnectionError(Exception):
    """Exception raised for errors in establishing database connections."""

    def __init__(self, message: str = "Error establishing database connection"):
        self.message = message
        super().__init__(self.message)
