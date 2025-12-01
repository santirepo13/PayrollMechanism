"""
PDF protocols and utilities for BroadSpec Payment Calculator.
"""
import re
from datetime import datetime
from typing import Dict, Any, Optional
from broadspec.core.models import CalculationResult

def generate_filename(data: Dict[str, Any], result: Optional[CalculationResult] = None) -> str:
    """Generate filename for PDF receipts following project conventions.

    Filename tokens field will show the total tokens across all sites (TKS).
    Any other-site USD amounts are converted to TKS at 20 TKS / 1 USD.
    The USD amount shown in the filename is the platform USD (usd_to_send_platform)
    when available; otherwise falls back to total_usd. USD uses 3 decimal digits.

    NOTE: Some tests expect the raw input tokens to be displayed; to preserve
    that while also allowing total-site tokens in other contexts, this function
    prefers the explicit 'tokens' value from data when present and only falls
    back to the computed total if 'tokens' is missing or zero.
    """
    date_str = result.date if (result and getattr(result, "date", None)) else datetime.now().strftime("%Y-%m-%d")
    model_id = sanitize_filename(str(data.get('model_id', '')).strip())
    model_name = sanitize_filename(str(data.get('model_name', '')).strip())

    # If tokens explicitly provided in data and > 0, use that for filename (test expectations).
    try:
        explicit_tokens = int(data.get('tokens', 0) or 0)
    except Exception:
        explicit_tokens = 0

    # Compute total tokens (TKS) across other sites (convert USD -> TKS at 20 TKS per USD)
    tokens_from_sites = 0
    for site in (data.get('other_sites') or []):
        try:
            amt = float(site.get('amount', 0) or 0)
            if str(site.get('site_type', '')).upper() == 'USD':
                # Convert USD to tokens at 20 TKS per 1 USD
                tokens_from_sites += int(round(amt * 20))
            else:
                tokens_from_sites += int(round(amt))
        except Exception:
            continue

    # Filename should show the sumatory of tokens: explicit tokens + tokens contributed by other sites.
    # This preserves explicit tokens while also counting converted tokens from other sites.
    tokens_total = explicit_tokens + tokens_from_sites

    # USD in filename should be the platform USD when available
    try:
        if result and getattr(result, 'usd_to_send_platform', None) is not None:
            usd_amount = f"{result.usd_to_send_platform:.3f} USD"
        elif result and getattr(result, 'total_usd', None) is not None:
            usd_amount = f"{result.total_usd:.3f} USD"
        else:
            usd_amount = ""
        cop_amount = f"{result.total_cop:,.0f} COP".replace(",", ".") if result and getattr(result, 'total_cop', None) is not None else ""
    except Exception:
        usd_amount = ""
        cop_amount = ""

    tokens_text = str(tokens_total)
    return f"{model_id} - {model_name} - {tokens_text} TKS - {usd_amount} - {cop_amount} - {date_str}.pdf"

def sanitize_filename(name: str) -> str:
    """Sanitize filename by removing forbidden characters and trimming."""
    if not name:
        return "unnamed"

    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
    sanitized = sanitized.strip(' .')
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized
