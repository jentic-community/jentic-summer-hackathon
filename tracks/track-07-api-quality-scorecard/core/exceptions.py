"""Custom exceptions for API Quality Scorecard."""


class ScorecardError(Exception):
    """Base exception for all scorecard-related errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ParseError(ScorecardError):
    """Raised when OpenAPI specification parsing fails."""
    
    def __init__(self, message: str, file_path: str = None, line_number: int = None):
        super().__init__(message)
        self.file_path = file_path
        self.line_number = line_number


class ValidationError(ScorecardError):
    """Raised when OpenAPI specification validation fails."""
    
    def __init__(self, message: str, validation_errors: list = None):
        super().__init__(message)
        self.validation_errors = validation_errors or []


class AnalysisError(ScorecardError):
    """Raised when quality analysis encounters an error."""
    
    def __init__(self, message: str, category: str = None, operation_id: str = None):
        super().__init__(message)
        self.category = category
        self.operation_id = operation_id


class ConfigurationError(ScorecardError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message)
        self.config_key = config_key


class ReportGenerationError(ScorecardError):
    """Raised when report generation fails."""
    
    def __init__(self, message: str, format_type: str = None):
        super().__init__(message)
        self.format_type = format_type