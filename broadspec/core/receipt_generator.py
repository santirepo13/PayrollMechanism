"""
PDF receipt generation for BroadSpec Payment Calculator.
"""
import os
from typing import Dict, Any
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .models import CalculationResult
from broadspec.utils.formatters import format_currency_cop, format_currency_usd
from broadspec.utils.pdf_protocols import generate_filename
from .exceptions import ReceiptGenerationError


class ReceiptGenerator:
    """Handles PDF receipt generation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize receipt generator with configuration."""
        self.config = config or {}
        self.receipts_path = self.config.get('storage', {}).get('receipts_path', 'Receipts')
    
    def generate_pdf(self, data: Dict[str, Any], result: CalculationResult) -> str:
        """
        Generate PDF receipt and return the file path.
        
        """
        try:
            # Ensure receipts directory exists
            os.makedirs(self.receipts_path, exist_ok=True)
            
            # Generate filename
            filename = generate_filename(data, result)
            filepath = os.path.join(self.receipts_path, filename)
            
            # Create PDF
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            
            # Add title
            c.setFont("Courier-Bold", 16)
            c.drawString(50, height - 50, "BROADSPEC PAYMENT RECEIPTS")
            
            # Add full receipt
            self._add_full_receipt(c, data, result, width, height)
            
            # New page for simple receipt
            c.showPage()
            self._add_simple_receipt(c, data, result, width, height)
            
            c.save()
            
            return filepath
            
        except Exception as e:
            raise ReceiptGenerationError(f"Failed to generate PDF: {str(e)}")
    
    def _add_full_receipt(self, c: canvas.Canvas, data: Dict[str, Any], 
                         result: CalculationResult, width: float, height: float):
        """Add full receipt to PDF."""
        c.setFont("Courier", 9)
        y_position = height - 100
        
        # Generate receipt content
        receipt_lines = self._generate_full_receipt_lines(data, result)
        
        for line in receipt_lines:
            if y_position < 100:
                c.showPage()
                y_position = height - 50
            c.drawString(50, y_position, line[:80])
            y_position -= 12
    
    def _add_simple_receipt(self, c: canvas.Canvas, data: Dict[str, Any], 
                          result: CalculationResult, width: float, height: float):
        """Add simple receipt to PDF."""
        c.setFont("Courier-Bold", 14)
        c.drawString(50, height - 50, "MODEL RECEIPT")
        
        c.setFont("Courier", 10)
        y_position = height - 100
        
        # Generate simple receipt content
        receipt_lines = self._generate_simple_receipt_lines(data, result)
        
        for line in receipt_lines:
            if y_position < 100:
                break
            c.drawString(50, y_position, line[:80])
            y_position -= 14
    
    def _generate_full_receipt_lines(self, data: Dict[str, Any], 
                                   result: CalculationResult) -> list[str]:
        """Generate lines for full receipt."""
        equals_line = "=" * 50
        
        # Format other sites display
        other_sites_display = self._format_other_sites_full(data)
        
        # Format advances display
        advances_display = self._format_advances_full(data)
        
        # Format fines display
        fines_display = result.fines_display if result.show_fines else "Fines: Disabled (Home Worker)"
        
        lines = [
            f"{equals_line}",
            "            PAYMENT RECEIPT",
            "              BROADSPEC",
            f"{equals_line}",
            f"Model ID: {data.get('model_id', '')}",
            f"Model: {data.get('model_name', '')}",
            f"Date: {result.date}",
            f"{equals_line}",
            "",
            "INPUT VALUES:",
            f"  TRM Official: {format_currency_cop(data.get('trm_official_cop', 0))}",
            f"  TRM BroadSpec: {format_currency_cop(result.trm_broadspec_cop)}",
            f"  Tokens (TKS): {data.get('tokens', 0):,}",
            f"  Percentage: {data.get('percentage', 0):.0%}",
            "  Other Sites (USD equivalent):",
        ]
        
        lines.extend(other_sites_display)
        lines.extend([
            f"  Previous Fortnight USD: {format_currency_usd(data.get('previous_fortnight_usd', 0))}",
            "",
            "ADVANCES:",
        ])
        
        lines.extend(advances_display)
        lines.append(f"  Total: {format_currency_cop(result.advances_total)}")
        lines.extend([
            "",
            "FINES:",
            f"  {fines_display}",
            "",
            "CALCULATED VALUES:",
            f"  USD from Tokens: {format_currency_usd(result.usd_from_tokens)}",
            f"  Net Amount USD: {format_currency_usd(result.net_usd)}",
            f"  Total USD (Pre-calc): {format_currency_usd(result.total_usd_precalc)}",
            f"  Total USD in COP: {format_currency_cop(result.total_usd_precalc * result.trm_broadspec_cop)}",
            f"  Transfer Cost: {format_currency_cop(result.transfer_cost_cop)}",
            "",
            "FINAL CALCULATION:",
            f"  BroadSpec Value: {format_currency_cop(result.valor_broadspec_cop)}",
            f"  Less Advances: {format_currency_cop(result.advances_total)}",
            f"  Less Fines: {format_currency_cop(result.fines_total)}",
            "",
            f"  TOTAL PAYMENT: {format_currency_cop(result.total_cop)}",
            f"  TOTAL PAYMENT: {format_currency_usd(result.total_usd)} USD",
            "",
            f"{equals_line}",
            "     Payment calculation completed",
            f"{equals_line}",
        ])
        
        return lines
    
    def _generate_simple_receipt_lines(self, data: Dict[str, Any], 
                                     result: CalculationResult) -> list[str]:
        """Generate lines for simple receipt."""
        equals_line = "=" * 40
        
        # Format other sites display
        other_sites_display = self._format_other_sites_simple(data)
        
        # Format advances display
        advances_display = self._format_advances_simple(data)
        
        # Format fines section
        fines_section = ""
        if result.show_fines:
            fines_section = f"Fines: {format_currency_cop(result.fines_total)} COP\n\n"
        
        lines = [
            "",
            "",
            "        BROADSPEC",
            "      Payment Summary",
            "",
            "",
            f"{equals_line}",
            "",
            f"Date: {result.date}",
            "",
            f"ID: {data.get('model_id', '')}",
            "",
            f"Model: {data.get('model_name', '')}",
            "",
            f"TRM Official: {format_currency_cop(data.get('trm_official_cop', 0))}",
            "",
            f"TRM BroadSpec: {format_currency_cop(result.trm_broadspec_cop)}",
            "",
            f"Tokens: {data.get('tokens', 0):,}",
            "",
            "Other Sites:",
        ]
        
        lines.extend(other_sites_display)
        lines.extend([
            "",
            f"Percentage: {data.get('percentage', 0):.0%}",
            "",
            "Advances:",
        ])
        
        lines.extend(advances_display)
        
        if fines_section:
            lines.append(fines_section)
        
        lines.extend([
            f"Total Payment: {format_currency_cop(result.total_cop)}",
            "",
            f"{equals_line}",
            "",
            "",
        ])
        
        return lines
    
    def _format_other_sites_full(self, data: Dict[str, Any]) -> list[str]:
        """Format other sites for full receipt."""
        other_sites = data.get('other_sites', [])
        if not other_sites:
            return ["    None"]
        
        lines = []
        for i, site in enumerate(other_sites, start=2):
            if site.get('site_type', '').upper() == 'USD':
                lines.append(f"    Site {i}: {format_currency_usd(site.get('amount', 0))} USD")
            else:
                usd_amt = site.get('amount', 0) / 20.0
                lines.append(f"    Site {i}: {int(site.get('amount', 0)):,} TKS => {format_currency_usd(usd_amt)} USD")
        
        return lines
    
    def _format_other_sites_simple(self, data: Dict[str, Any]) -> list[str]:
        """Format other sites for simple receipt."""
        other_sites = data.get('other_sites', [])
        if not other_sites:
            return ["  None"]
        
        lines = []
        for i, site in enumerate(other_sites, start=2):
            if site.get('site_type', '').upper() == 'USD':
                lines.append(f"  Site {i}: {format_currency_usd(site.get('amount', 0))}")
            else:
                lines.append(f"  Site {i}: {int(site.get('amount', 0)):,} TKS")
        
        return lines
    
    def _format_advances_full(self, data: Dict[str, Any]) -> list[str]:
        """Format advances for full receipt."""
        advances = data.get('advances', [])
        if not advances:
            return ["    None\n"]
        
        lines = []
        for advance in advances:
            lines.append(f"    {advance.get('date', '')}: {format_currency_cop(advance.get('amount', 0))} COP")
        
        lines.append("")  # Empty line after advances
        return lines
    
    def _format_advances_simple(self, data: Dict[str, Any]) -> list[str]:
        """Format advances for simple receipt."""
        advances = data.get('advances', [])
        if not advances:
            return ["  None\n"]
        
        lines = []
        for advance in advances:
            lines.append(f"  {advance.get('date', '')}: {format_currency_cop(advance.get('amount', 0), show_decimals=False)}")
        
        return lines
