"""
Payment calculation logic for BroadSpec Payment Calculator.
"""
from typing import List
from .models import PaymentData, CalculationResult, OtherSite, Advance


class PaymentCalculator:
    """Handles all payment calculations."""
    
    def __init__(self, config: dict = None):
        """Initialize calculator with configuration."""
        self.config = config or {}
        self.token_to_usd_rate = self.config.get('calculation', {}).get('token_to_usd_rate', 20.0)
        self.trm_adjustment = self.config.get('calculation', {}).get('trm_adjustment', 300)
        self.fine_amount = self.config.get('calculation', {}).get('fine_amount', 30000)
        self.transfer_cost = self.config.get('app', {}).get('transfer_cost', 6.99)
        self.transfer_cost_tax = self.config.get('calculation', {}).get('transfer_cost_tax', 0.19)
    
    def calculate(self, data: PaymentData) -> CalculationResult:
        """Perform payment calculation."""
        # Calculate TRM values
        trm_broadspec_cop = data.trm_official_cop - self.trm_adjustment
        
        # Calculate transfer cost
        transfer_cost_usd = self.transfer_cost + (self.transfer_cost * self.transfer_cost_tax)
        transfer_cost_cop = transfer_cost_usd * data.btk_trm_cop
        
        # Calculate USD values
        usd_from_tokens = data.tokens / self.token_to_usd_rate
        percent = data.percentage
        if percent > 1:
            percent = percent / 100.0
        net_usd = usd_from_tokens * percent

        # Calculate total USD for other sites
        other_sites_total_usd = sum(site.get_usd_equivalent() for site in data.other_sites) * percent
        
        
        # Calculate total USD before final calculation
        total_usd_precalc = net_usd + other_sites_total_usd + data.previous_fortnight_usd
        
        # Calculate BroadSpec value in COP
        valor_broadspec_cop = (total_usd_precalc * trm_broadspec_cop) - transfer_cost_cop
        
        # Calculate fines
        fines_total, fines_display, show_fines = self._calculate_fines(data)
        
        # Calculate advances total
        advances_total = sum(advance.amount for advance in data.advances)
        
        # Calculate final payment
        total_cop = valor_broadspec_cop - advances_total - fines_total
        total_usd = total_cop / trm_broadspec_cop
        
        return CalculationResult(
            total_cop=total_cop,
            total_usd=total_usd,
            trm_broadspec_cop=trm_broadspec_cop,
            transfer_cost_cop=transfer_cost_cop,
            valor_broadspec_cop=valor_broadspec_cop,
            fines_total=fines_total,
            fines_display=fines_display,
            show_fines=show_fines,
            advances_total=advances_total,
            other_sites_total_usd=other_sites_total_usd,
            usd_from_tokens=usd_from_tokens,
            net_usd=net_usd,
            total_usd_precalc=total_usd_precalc,
            date=data.date if hasattr(data, 'date') else ""
        )
    
    def _calculate_fines(self, data: PaymentData) -> tuple[float, str, bool]:
        """Calculate fines based on percentage and input values."""
        percent = data.percentage
        if percent > 1:
            percent = percent / 100.0
        show_fines = percent <= 0.60
        
        if data.custom_fine_cop > 0:
            fines_total = data.custom_fine_cop
            fines_display = f"Custom: {fines_total:,.0f} COP"
        else:
            fines_total = data.fines_count * self.fine_amount
            fines_display = f"{data.fines_count} fines x {self.fine_amount:,} = {fines_total:,.0f} COP"
        
        return fines_total, fines_display, show_fines
    
    def validate_data(self, data: PaymentData) -> List[str]:
        """Validate payment data and return list of errors."""
        errors = []
        
        if not data.model_id.strip():
            errors.append("Model ID is required")
        
        if data.trm_official_cop <= 0:
            errors.append("TRM Official COP must be greater than 0")
        
        if data.btk_trm_cop <= 0:
            errors.append("BTK TRM COP must be greater than 0")
        
        if data.tokens < 0:
            errors.append("Tokens cannot be negative")
        
        percent = data.percentage
        if percent > 1:
            percent = percent / 100.0
        if percent <= 0 or percent > 1:
            errors.append("Percentage must be between 0 and 1")
        
        if data.previous_fortnight_usd < 0:
            errors.append("Previous Fortnight USD cannot be negative")
        
        if data.fines_count < 0:
            errors.append("Fines count cannot be negative")
        
        if data.custom_fine_cop < 0:
            errors.append("Custom fine amount cannot be negative")
        
        for i, advance in enumerate(data.advances):
            if advance.amount < 0:
                errors.append(f"Advance {i+1} amount cannot be negative")
        
        for i, site in enumerate(data.other_sites):
            if site.amount < 0:
                errors.append(f"Other Site {i+1} amount cannot be negative")
            if site.site_type not in ['USD', 'TKS']:
                errors.append(f"Other Site {i+1} type must be USD or TKS")
        
        return errors
