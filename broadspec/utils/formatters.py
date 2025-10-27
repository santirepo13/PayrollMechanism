"""
Text formatting utilities for BroadSpec Payment Calculator.
"""
import re
import os
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from broadspec.core.models import PaymentData, CalculationResult


def sanitize_filename(name: str) -> str:
    """Sanitize filename by removing characters forbidden on Windows while preserving Unicode accents."""
    if not name:
        return "unnamed"
    # Replace forbidden characters <>:"/\|?* and control characters with underscore
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
    # Remove trailing spaces and dots (not allowed on Windows)
    sanitized = sanitized.rstrip(' .')
    return sanitized


def human_readable_size(num_bytes: int) -> str:
    """Return human readable size string for bytes"""
    try:
        for unit in ['B','KB','MB','GB','TB']:
            if num_bytes < 1024.0:
                return f"{num_bytes:3.1f} {unit}"
            num_bytes /= 1024.0
        return f"{num_bytes:.1f} PB"
    except Exception:
        return f"{num_bytes} B"


def parse_filename_metadata(filename: str) -> Dict[str, str]:
    """Extract model_id, model_name, tokens, date from common filename patterns.

    Handles filenames produced by the app as well as imported/legacy names.
    Returns empty strings for missing fields.
    """
    try:
        if not filename:
            return {"model_id": "", "model_name": "", "tokens": "", "date": ""}
        base = os.path.basename(filename)
        base = base.rsplit(".pdf", 1)[0]
        # detect ISO date at end (YYYY-MM-DD)
        date = ""
        m = re.search(r'(\d{4}-\d{2}-\d{2})$', base)
        if m:
            date = m.group(1)
            base_wo_date = base[:m.start()].rstrip(' -')
        else:
            base_wo_date = base
        # split parts, preserving parts that may contain " - " inside a name by trimming empties
        parts = [p.strip() for p in base_wo_date.split(" - ") if p.strip() != ""]
        model_id = parts[0] if len(parts) >= 1 else ""
        tokens = ""
        model_name = ""
        # scan from right for a token-like segment (e.g. '5000 TKS' or just '2609')
        token_index = None
        for i in range(len(parts) - 1, 0, -1):
            if re.search(r'\b\d[\d,\.]*\s*(TKS)?\b', parts[i], re.IGNORECASE):
                token_index = i
                break
        if token_index is not None:
            tokens = parts[token_index]
            if token_index > 1:
                model_name = " - ".join(parts[1:token_index])
            else:
                model_name = parts[1] if len(parts) > 1 else ""
        else:
            if len(parts) >= 3:
                tokens = parts[-1]
                model_name = " - ".join(parts[1:-1])
            else:
                tokens = ""
                model_name = " - ".join(parts[1:]) if len(parts) > 1 else ""
        return {"model_id": model_id, "model_name": model_name, "tokens": tokens, "date": date}
    except Exception:
        return {"model_id": "", "model_name": "", "tokens": "", "date": ""}


def format_currency(amount: float, currency: str = "COP") -> str:
    """Format currency amount with appropriate separators."""
    if currency.upper() == "USD":
        return f"${amount:,.2f} USD"
    else:  # COP
        return f"{amount:,.0f} COP"


def format_currency_cop(amount: float, show_decimals: bool = True) -> str:
    """Format COP currency amount."""
    if show_decimals:
        return f"{amount:,.2f} COP"
    else:
        return f"{amount:,.0f} COP"


def format_currency_usd(amount: float) -> str:
    """Format USD currency amount."""
    return f"${amount:,.2f}"


def format_full_receipt(result: 'CalculationResult', data: 'PaymentData') -> str:
    """Generate full receipt text."""
    equals_line = "=" * 50
    
    # Generate other sites display
    other_sites_lines = []
    for i, site in enumerate(data.other_sites, start=2):
        if site.site_type.upper() == 'USD':
            other_sites_lines.append(f"    Site {i}: ${site.amount:,.2f} USD")
        else:
            usd_equiv = site.get_usd_equivalent()
            other_sites_lines.append(f"    Site {i}: {int(site.amount):,} TKS => ${usd_equiv:,.2f} USD")
    
    other_sites_display = "\n".join(other_sites_lines) if other_sites_lines else "    None"
    
    # Generate advances display
    advances_lines = []
    for advance in data.advances:
        advances_lines.append(f"    {advance.date}: {format_currency_cop(advance.amount)}")
    advances_display = "\n".join(advances_lines) if advances_lines else "    None"
    
    return f"""
{equals_line}
            PAYMENT RECEIPT
              BROADSPEC
{equals_line}
Model ID: {data.model_id}
Model: {data.model_name}
Date: {result.date}
{equals_line}
  
INPUT VALUES:
  TRM Official $COP: {data.trm_official_cop:,.2f}
  TRM BROADSPEC $COP: {result.trm_broadspec_cop:,.2f}
  Tokens (TKS): {data.tokens:,}
  Percentage: {data.percentage:.0%}
  Other Sites (USD equivalent):
{other_sites_display}
  Previous Fortnight USD: ${data.previous_fortnight_usd:,.2f} USD
  
ADVANCES:
{advances_display}
  Total: {format_currency_cop(result.advances_total)}
  
FINES:
  {result.fines_display}
  
CALCULATED VALUES:
  USD from Tokens: ${result.usd_from_tokens:,.2f} USD
  Net Amount USD: ${result.net_usd:,.2f} USD
  Total USD (Pre-calc): ${result.total_usd_precalc:,.2f} USD
  Total USD in COP: {format_currency_cop(result.total_usd_precalc * result.trm_broadspec_cop)}
  Transfer Cost: {format_currency_cop(result.transfer_cost_cop)}
  
FINAL CALCULATION:
  BroadSpec Value: {format_currency_cop(result.valor_broadspec_cop)}
  Less Advances: {format_currency_cop(result.advances_total)}
  Less Fines: {format_currency_cop(result.fines_total)}
   
  TOTAL PAYMENT: {format_currency_cop(result.total_cop)}
  TOTAL PAYMENT: ${result.total_usd:,.2f} USD
 
{equals_line}
     Payment calculation completed
{equals_line}
"""


def format_simple_receipt(result: 'CalculationResult', data: 'PaymentData') -> str:
    """Generate simplified receipt text."""
    equals_line = "=" * 40
    
    # Generate other sites display for simple receipt
    other_sites_lines = []
    for i, site in enumerate(data.other_sites, start=2):
        if site.site_type.upper() == 'USD':
            other_sites_lines.append(f"  Site {i}: ${site.amount:,.2f}")
        else:
            other_sites_lines.append(f"  Site {i}: {int(site.amount):,} TKS")
    
    other_sites_display = "\n".join(other_sites_lines) if other_sites_lines else "  None"
    
    # Generate advances display for simple receipt
    advances_lines = []
    for advance in data.advances:
        advances_lines.append(f"  {advance.date}: {format_currency_cop(advance.amount, show_decimals=False)}")
    advances_display = "\n".join(advances_lines) if advances_lines else "  None"
    
    # Include fines section only if applicable
    fines_section = ""
    if result.show_fines:
        fines_section = f"Fines: {format_currency_cop(result.fines_total, show_decimals=False)}" + "\n\n"
    
    return f"""
    
    
    
        BROADSPEC
      Payment Summary
   
   
   
{equals_line}
 
Date: {result.date}
 
ID: {data.model_id}
 
Model: {data.model_name}
 
TRM Official: {format_currency_cop(data.trm_official_cop)}
  
TRM BroadSpec: {format_currency_cop(result.trm_broadspec_cop)}
 
Tokens: {data.tokens:,}
 
Other Sites:
{other_sites_display}
 
Percentage: {data.percentage:.0%}
 
Advances:
{advances_display}
{fines_section}Total Payment:
{format_currency_cop(result.total_cop)}
 
{equals_line}
  
  
"""