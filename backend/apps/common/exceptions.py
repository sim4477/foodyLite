# Custom exceptions for the Food Delivery App

class ServiceError(Exception):
    """Base exception for service layer errors"""

    def __init__(self, message, errors=None, status_code=400):
        self.message = message
        self.errors = errors or {}
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(ServiceError):
    """Authentication related errors"""

    def __init__(self, message="Authentication failed"):
        super().__init__(message, status_code=401)

class PermissionError(ServiceError):
    """Permission related errors"""

    def __init__(self, message="Permission denied"):
        super().__init__(message, status_code=403)

class ValidationError(ServiceError):
    """Validation related errors"""

    def __init__(self, message="Validation failed", errors=None):
        super().__init__(message, errors, status_code=400)

class NotFoundError(ServiceError):
    """Resource not found errors"""

    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)

class BookingError(ServiceError):
    """Booking specific errors"""
    pass

class ChatError(ServiceError):
    """Chat specific errors"""
    pass
