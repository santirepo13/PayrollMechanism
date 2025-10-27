"""
PDF protocols and utilities for BroadSpec Payment Calculator.
"""
import re
from datetime import datetime
from typing import Dict, Any, Optional

from broadspec.core.models import CalculationResult


def generate_filename(data: Dict[str, Any], result: Optional[CalculationResult] = None) -> str:
    """Generate filename for PDF."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    model_id = sanitize_filename(data.get('model_id', ''))
    model_name = sanitize_filename(data.get('model_name', ''))
    tokens = data.get('tokens', '')
    
    # Add USD and COP amounts if result is provided
    usd_amount = ""
    cop_amount = ""
    if result:
        usd_amount = f"{result.total_usd:.2f} USD"
        cop_amount = f"{result.total_cop:,.0f} COP".replace(",", ".")
    
    return f"{model_id} - {model_name} - {tokens} TKS - {usd_amount} - {cop_amount} - {date_str}.pdf"


def sanitize_filename(name: str) -> str:
    """Sanitize filename by removing forbidden characters."""
    if not name:
        return "unnamed"
    
    # Replace forbidden characters with underscore
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
    # Remove trailing spaces and dots
    sanitized = sanitized.rstrip(' .')
    return sanitized