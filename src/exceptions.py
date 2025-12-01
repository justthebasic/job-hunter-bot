class JobHunterError(Exception):
    """Base exception for Job Hunter Bot."""
    pass

class NavigationError(JobHunterError):
    """Raised when browser navigation fails."""
    pass

class ExtractionError(JobHunterError):
    """Raised when data extraction fails."""
    pass

class PDFGenerationError(JobHunterError):
    """Raised when PDF generation fails."""
    pass

class ConfigurationError(JobHunterError):
    """Raised when configuration is invalid."""
    pass
