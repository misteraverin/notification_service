class EntityDoesNotExist(Exception):
    """Raised when entity was not found in database."""
    pass


class PhoneCodeError(Exception):
    """Raised when phone code is not a string of 3 digits."""
    pass


class PhoneError(Exception):
    """Raised when phone is not a string of 7 digits."""
    pass


class TimezoneError(Exception):
    """Raised when input timezone is not in the list of timezones."""
    pass


class UserCredentialsError(Exception):
    """Raised when username or password are incorrect."""
    pass


class WrongDatetimeError(Exception):
    """Raised when finish time is less than start time."""
    pass
