"""
Custom exception classes for BroadSpec Payment Calculator.
"""


class BroadSpecError(Exception):
    """Base exception for application"""
    pass


class CalculationError(BroadSpecError):
    """Errors in payment calculations"""
    pass


class ReceiptGenerationError(BroadSpecError):
    """Errors in receipt (PDF) generation"""
    pass


class VaultError(BroadSpecError):
    """Errors in vault operations"""
    pass


class UIError(BroadSpecError):
    """Errors in UI operations"""
    pass


class ValidationError(BroadSpecError):
    """Errors in input validation"""
    pass


class ConfigurationError(BroadSpecError):
    """Errors in configuration loading"""
    pass


class StorageError(BroadSpecError):
    """Errors in file storage operations"""
    pass


class ReceiptGenerationError(BroadSpecError):
    """Errors in PDF receipt generation"""
    pass


class ValidationError(BroadSpecError):
    """Errors in data validation"""
    pass