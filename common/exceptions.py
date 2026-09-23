"""
Custom exceptions + a single register_error_handlers(app) call that
every service uses, equivalent to the Java @RestControllerAdvice
GlobalExceptionHandler.
"""
from marshmallow import ValidationError
from common.responses import error


class ResourceNotFoundException(Exception):
    def __init__(self, resource: str, field: str, value):
        self.message = f"{resource} not found with {field}: {value}"
        super().__init__(self.message)


class BusinessException(Exception):
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def register_error_handlers(app):
    """Attach uniform JSON error handling to a Flask app instance."""

    @app.errorhandler(ResourceNotFoundException)
    def handle_not_found(exc: ResourceNotFoundException):
        return error(exc.message, error_code="RESOURCE_NOT_FOUND", status_code=404)

    @app.errorhandler(BusinessException)
    def handle_business_error(exc: BusinessException):
        return error(exc.message, error_code=exc.error_code, status_code=400)

    @app.errorhandler(ValidationError)
    def handle_validation_error(exc: ValidationError):
        return error(
            "Validation failed",
            error_code="VALIDATION_ERROR",
            status_code=400,
            field_errors=exc.messages if isinstance(exc.messages, dict) else {"_": exc.messages},
        )

    @app.errorhandler(404)
    def handle_404(exc):
        return error("Resource not found", error_code="NOT_FOUND", status_code=404)

    @app.errorhandler(Exception)
    def handle_generic(exc: Exception):
        app.logger.exception("Unhandled exception")
        return error(str(exc), error_code="INTERNAL_SERVER_ERROR", status_code=500)
