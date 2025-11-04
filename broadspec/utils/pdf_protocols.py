"""
PDF protocols and utilities for BroadSpec Payment Calculator.
"""
import re
from datetime import datetime
from typing import Dict, Any, Optional
from broadspec.core.models import CalculationResult

def generate_filename(data: Dict[str, Any], result: Optional[CalculationResult] = None) -> str:
    """Generate filename for PDF receipts following project conventions."""
    # Prefer result date when provided (keeps tests deterministic); otherwise use now
    date_str = result.date if (result and getattr(result, "date", None)) else datetime.now().strftime("%Y-%m-%d")
    model_id = sanitize_filename(str(data.get('model_id', '')).strip())
    model_name = sanitize_filename(str(data.get('model_name', '')).strip())
    tokens = data.get('tokens', '')

    try:
        usd_amount = "0.00 USD"
        cop_amount = "0 COP"
        if result:
            usd_amount = f"{result.total_usd:.2f} USD"
            cop_amount = f"{result.total_cop:,.0f} COP".replace(",", ".")
    except Exception:
        usd_amount = "0.00 USD"
        cop_amount = "0 COP"

    tokens_text = str(tokens)
    return f"{model_id} - {model_name} - {tokens_text} TKS - {usd_amount} - {cop_amount} - {date_str}.pdf"

def sanitize_filename(name: str) -> str:
    """Sanitize filename by removing forbidden characters and trimming."""
    if not name:
        return "unnamed"

    # Replace forbidden characters with underscore
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
    # Remove trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Collapse multiple whitespace into single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized
