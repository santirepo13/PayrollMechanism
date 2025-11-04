"""
Calculation handler component for BroadSpec Payment Calculator.
"""
import tkinter as tk
from tkinter import messagebox

from broadspec.core.exceptions import BroadSpecError


class CalculationHandler:
    """Handles payment calculation functionality."""
    
    def __init__(self, main_tab_ui, window_setup, controller):
        """Initialize calculation handler."""
        self.main_tab_ui = main_tab_ui
        self.window_setup = window_setup
        self.controller = controller
        
        # Set the calculate button command directly
        self.main_tab_ui.calculate_btn.config(command=self.calculate)
    
    def calculate(self):
        """Perform payment calculation."""
        try:
            form_data = self._get_form_data()
            input_data, result_data = self.controller.calculate_payment(form_data)
            self.window_setup.current_input_data = input_data
            self.window_setup.current_result_data = result_data
            self._display_receipts(input_data, result_data)
        except BroadSpecError as e:
            messagebox.showerror("Calculation Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")
    
    def _get_form_data(self) -> dict:
        """Collect data from form fields."""
        # Get other sites
        other_sites = []
        for type_cb, amount_e, _ in getattr(self.main_tab_ui, 'other_sites_entries', []):
            try:
                amount = float(amount_e.get() or 0)
                if amount > 0:
                    other_sites.append({
                        'site_type': type_cb.get(),
                        'amount': amount
                    })
            except ValueError:
                pass
        
        # Get advances
        advances = []
        for date_e, amount_e, _ in self.main_tab_ui.advances_entries:
            try:
                amount = float(amount_e.get() or 0)
                advances.append({
                    'date': date_e.get(),
                    'amount': amount
                })
            except ValueError:
                pass
        
        # Get fines
        custom_fine = (self.main_tab_ui.custom_fine_cop.get() or "").strip().replace(",", "")
        if custom_fine:
            fines_count = 0
            custom_fine_cop = float(custom_fine)
        else:
            fines_count = int(self.main_tab_ui.fines_count.get() or 0)
            custom_fine_cop = 0
        
        # Get percentage
        perc_str = self.main_tab_ui.percentage.get()
        percentage = float(perc_str.strip('%')) / 100
        
        return {
            'model_id': self.main_tab_ui.model_id.get().strip(),
            'model_name': self.main_tab_ui.model_name.get(),
            'trm_official_cop': float(self.main_tab_ui.trm_official_cop.get()),
            'btk_trm_cop': float(self.main_tab_ui.btk_trm_cop.get()),
            'tokens': int(self.main_tab_ui.tokens.get()),
            'percentage': percentage,
            'previous_fortnight_usd': float(self.main_tab_ui.previous_fortnight_usd.get() or 0),
            'other_sites': other_sites,
            'advances': advances,
            'fines_count': fines_count,
            'custom_fine_cop': custom_fine_cop
        }
    
    def _display_receipts(self, input_data: dict, result_data: dict):
        """Display calculation results in both receipt text areas."""
        # Generate full receipt for display
        full_receipt = self._generate_full_receipt(input_data, result_data)
        self.main_tab_ui.receipt_text.delete(1.0, tk.END)
        self.main_tab_ui.receipt_text.insert(1.0, full_receipt)
        
        # Generate model screenshot for payment confirmation
        model_receipt = self._generate_model_receipt(input_data, result_data)
        self.main_tab_ui.model_text.delete(1.0, tk.END)
        self.main_tab_ui.model_text.insert(1.0, model_receipt)
    
    def _generate_full_receipt(self, input_data: dict, result_data: dict) -> str:
        """Generate full receipt text."""
        equals_line = "=" * 50
        
        # Format other sites
        other_sites_lines = []
        for i, site in enumerate(input_data.get('other_sites', []), start=2):
            if site['site_type'] == 'USD':
                other_sites_lines.append(f"    Site {i}: {site['amount']:,.2f} USD")
            else:
                usd_amt = site['amount'] / 20.0
                other_sites_lines.append(f"    Site {i}: {int(site['amount']):,} TKS => {usd_amt:,.2f} USD")
        
        other_sites_display = "\n".join(other_sites_lines) if other_sites_lines else "    None"
        
        # Format advances
        advances_lines = []
        for advance in input_data.get('advances', []):
            advances_lines.append(f"    {advance['date']}: {advance['amount']:,.2f} COP")
        
        advances_display = "\n".join(advances_lines) if advances_lines else "    None"
        if advances_display:
            advances_display += "\n"
        
        # Build fines section: omit entirely when fines are not shown
        if result_data.get('show_fines', True):
            fines_display = result_data.get('fines_display', '')
            fines_section = f"\nFINES:\n  {fines_display}\n"
        else:
            fines_section = ""
        
        return f"""
{equals_line}
            PAYMENT RECEIPT
              BROADSPEC
{equals_line}
Model ID: {input_data.get('model_id', '')}
Model: {input_data.get('model_name', '')}
Date: {result_data.get('date', '')}
{equals_line}
  
INPUT VALUES:
  TRM Official $COP: {input_data.get('trm_official_cop', 0):,.2f} COP
  TRM BROADSPEC $COP: {result_data.get('trm_broadspec_cop', 0):,.2f} COP
  Tokens (TKS): {input_data.get('tokens', 0):,}
  Percentage: {input_data.get('percentage', 0):.0%}
  Other Sites (USD equivalent):
{other_sites_display}
  Previous Fortnight USD: {input_data.get('previous_fortnight_usd', 0):,.2f} USD
  
ADVANCES:
{advances_display}  Total: {result_data.get('advances_total', 0):,.2f} COP{fines_section}
CALCULATED VALUES:
  USD from Tokens: {result_data.get('usd_from_tokens', 0):,.2f} USD
  Net Amount USD: {result_data.get('net_usd', 0):,.2f} USD
  Total USD (Pre-calc): {result_data.get('total_usd_precalc', 0):,.2f} USD
  Total USD in COP: {result_data.get('total_usd_precalc', 0) * result_data.get('trm_broadspec_cop', 1):,.2f} COP
  Transfer Cost: {result_data.get('transfer_cost_cop', 0):,.2f} COP
  
FINAL CALCULATION:
  BroadSpec Value: {result_data.get('valor_broadspec_cop', 0):,.2f} COP
  Less Advances: {result_data.get('advances_total', 0):,.2f} COP
  Less Fines: {result_data.get('fines_total', 0):,.2f} COP
   
  TOTAL PAYMENT: {result_data.get('total_cop', 0):,.2f} COP
  TOTAL PAYMENT: {result_data.get('total_usd', 0):,.2f} USD
 
{equals_line}
     Payment calculation completed
{equals_line}
"""
    
    def _generate_model_receipt(self, input_data: dict, result_data: dict) -> str:
        width = 38
        header_lines = [
            "BROADSPEC".center(width),
            "Payment Summary".center(width)
        ]
        separator = "-" * width

        # Safe converters
        def safe_float(v, default=0.0):
            try:
                return float(v)
            except Exception:
                return default

        def safe_int(v, default=0):
            try:
                return int(v)
            except Exception:
                return default

        # Extract core fields with safe defaults
        date = result_data.get('date', '')
        model_id = input_data.get('model_id', '') or ''
        model_name = input_data.get('model_name', '') or ''
        trm_official = f"{safe_float(input_data.get('trm_official_cop', 0)):,.2f} COP"
        trm_broadspec = f"{safe_float(result_data.get('trm_broadspec_cop', 0)):,.2f} COP"
        tokens = f"{safe_int(input_data.get('tokens', 0)):,}"
        percentage = input_data.get('percentage', 0)

        # Other sites: include only entries with amount > 0, show USD or TKS accordingly
        other_sites_lines = []
        for i, site in enumerate(input_data.get('other_sites', []), start=2):
            amt = safe_float(site.get('amount', 0))
            if amt <= 0:
                continue
            if site.get('site_type') == 'USD':
                other_sites_lines.append(f"  Site {i}: {amt:,.2f} USD")
            else:
                other_sites_lines.append(f"  Site {i}: {int(amt):,} TKS")

        # Advances: include only advances with amount > 0
        advances_lines = []
        for adv in input_data.get('advances', []):
            amt = safe_float(adv.get('amount', 0))
            if amt > 0:
                adv_date = adv.get('date', '')
                advances_lines.append(f"  {adv_date}: {amt:,.2f} COP")

        # Build ordered receipt lines to match the provided example
        parts = []
        parts.extend(header_lines)
        parts.append("")  # blank line
        parts.append(separator)
        parts.append(f"Date: {date}")
        parts.append("")  # blank
        parts.append(f"ID: {model_id}")
        parts.append("")  # blank
        parts.append(f"Model: {model_name}")
        parts.append("")  # blank
        parts.append(f"TRM Official: {trm_official}")
        parts.append(f"TRM BroadSpec: {trm_broadspec}")
        parts.append("")  # blank
        parts.append(f"Tokens: {tokens}")
        parts.append("")  # blank
        parts.append("Other Sites:")
        # leave a blank line under Other Sites to match the visual example
        if other_sites_lines:
            parts.append("")  # blank
            parts.extend(other_sites_lines)
        else:
            parts.append("")  # blank to indicate empty area

        parts.append("")  # blank
        parts.append(f"Percentage: {percentage:.0%}")

        # Only include Advances section if there are any positive advances
        if advances_lines:
            parts.append("")  # blank
            parts.append("Advances:")
            parts.extend(advances_lines)

        # Fines: show only when allowed
        if result_data.get('show_fines', True):
            parts.append("")  # blank
            parts.append(f"Fines: {safe_float(result_data.get('fines_total', 0)):,.2f} COP")

        parts.append("")  # blank
        parts.append("Total Payment:")
        parts.append(f"{safe_float(result_data.get('total_cop', 0)):,.2f} COP")
        parts.append("")  # blank
        parts.append(separator)

        # Return with leading/trailing newlines for consistent spacing in the text widget
        return "\n" + "\n".join(parts) + "\n"