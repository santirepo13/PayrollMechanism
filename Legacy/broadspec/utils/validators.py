"""
Input validation utilities for BroadSpec Payment Calculator.
"""
import re
from typing import List, Tuple


def validate_numeric_input(value: str, field_name: str, allow_zero: bool = True) -> Tuple[bool, str]:
    """Validate numeric input and return (is_valid, error_message)."""
    if not value.strip():
        return False, f"{field_name} is required"
    
    try:
        num_value = float(value.replace(",", ""))
        if not allow_zero and num_value <= 0:
            return False, f"{field_name} must be greater than 0"
        elif num_value < 0:
            return False, f"{field_name} cannot be negative"
        return True, ""
    except ValueError:
        return False, f"{field_name} must be a valid number"


def validate_integer_input(value: str, field_name: str, allow_zero: bool = True, min_value: int = None) -> Tuple[bool, str]:
    """Validate integer input and return (is_valid, error_message)."""
    if not value.strip():
        return False, f"{field_name} is required"
    
    try:
        int_value = int(value.replace(",", ""))
        if not allow_zero and int_value <= 0:
            return False, f"{field_name} must be greater than 0"
        elif int_value < 0:
            return False, f"{field_name} cannot be negative"
        if min_value is not None and int_value < min_value:
            return False, f"{field_name} must be at least {min_value}"
        return True, ""
    except ValueError:
        return False, f"{field_name} must be a valid integer"


def validate_text_input(value: str, field_name: str, required: bool = True, max_length: int = None) -> Tuple[bool, str]:
    """Validate text input and return (is_valid, error_message)."""
    if required and not value.strip():
        return False, f"{field_name} is required"
    
    if max_length is not None and len(value) > max_length:
        return False, f"{field_name} cannot exceed {max_length} characters"
    
    return True, ""


def validate_percentage(value: str) -> Tuple[bool, str]:
    """Validate percentage input (should be between 0 and 100)."""
    if not value.strip():
        return False, "Percentage is required"
    
    try:
        clean_value = value.strip().rstrip('%')
        percentage = float(clean_value)
        
        if percentage <= 0 or percentage > 100:
            return False, "Percentage must be between 0 and 100"
        
        return True, ""
    except ValueError:
        return False, "Percentage must be a valid number"


def validate_date(value: str) -> Tuple[bool, str]:
    """Validate date format (YYYY-MM-DD)."""
    if not value.strip():
        return False, "Date is required"
    
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, value):
        return False, "Date must be in YYYY-MM-DD format"
    
    return True, ""


def validate_model_id(value: str) -> Tuple[bool, str]:
    """Validate model ID format."""
    if not value.strip():
        return False, "Model ID is required"
    
    if not re.match(r'^[a-zA-Z0-9\-]+$', value.strip()):
        return False, "Model ID can only contain letters, numbers, and hyphens"
    
    return True, ""


def validate_site_type(value: str) -> Tuple[bool, str]:
    """Validate site type (USD or TKS)."""
    if value.upper() not in ['USD', 'TKS']:
        return False, "Site type must be USD or TKS"
    return True, ""
 


def sanitize_numeric_input(value: str) -> str:
    """Sanitize numeric input by removing commas and extra spaces."""
    return value.replace(",", "").strip()


def sanitize_text_input(value: str) -> str:
    """Sanitize text input by trimming whitespace."""
    return value.strip()


class ValidationErrors:
    """Container for validation errors."""
    
    def __init__(self):
        self.errors = []
    
    def add_error(self, field: str, message: str):
        """Add a validation error."""
        self.errors.append(f"{field}: {message}")
    
    def add_errors(self, errors: List[Tuple[str, str]]):
        """Add multiple validation errors."""
        for field, message in errors:
            self.add_error(field, message)
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[str]:
        """Get all error messages."""
        return self.errors
    
    def get_error_string(self) -> str:
        """Get all errors as a single string."""
        return "\n".join(self.errors)
    
    def clear(self):
        """Clear all errors."""
        self.errors = []


def validate_payment_data(payment_data):
    """Validate payment data and return list of errors."""
    errors = []
    
    if not payment_data.model_id:
        errors.append("Model ID is required")
    
    if not payment_data.model_name:
        errors.append("Model name is required")
    
    if payment_data.trm_official_cop <= 0:
        errors.append("TRM Official COP must be greater than 0")
    
    if payment_data.tokens <= 0:
        errors.append("Tokens must be greater than 0")
    
    if payment_data.percentage <= 0 or payment_data.percentage > 1:
        errors.append("Percentage must be between 0 and 100%")
    
    for i, site in enumerate(payment_data.other_sites):
        if site.amount < 0:
            errors.append(f"Other site {i+1} amount cannot be negative")
    
    for i, advance in enumerate(payment_data.advances):
        if advance.amount < 0:
            errors.append(f"Advance {i+1} amount cannot be negative")
    
    if payment_data.fines_count < 0:
        errors.append("Fines count cannot be negative")
    
    if payment_data.custom_fine_cop < 0:
        errors.append("Custom fine amount cannot be negative")
    
    return errors