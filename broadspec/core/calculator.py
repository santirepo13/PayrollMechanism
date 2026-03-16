from typing import List, Optional
from .models import PaymentData, CalculationResult, OtherSite, Advance
from datetime import datetime


class PaymentCalculator:
    """Handles all payment calculations."""
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize calculator with configuration."""
        self.config = config or {}
        self.token_to_usd_rate = self.config.get('calculation', {}).get('token_to_usd_rate', 20.0)
        self.trm_adjustment = self.config.get('calculation', {}).get('trm_adjustment', 300)
        self.fine_amount = self.config.get('calculation', {}).get('fine_amount', 30000)
        self.transfer_cost = self.config.get('app', {}).get('transfer_cost', 6.99)
        self.transfer_cost_tax = self.config.get('calculation', {}).get('transfer_cost_tax', 0.19)
    
    def calculate(self, data: PaymentData) -> CalculationResult:
        """Perform payment calculation."""
        # Determine total tokens across all sites before applying percentage
        # - Main tokens come as TKS directly
        # - Other sites can be USD or TKS; convert USD -> TKS using token_to_usd_rate (e.g., 1 USD = 20 TKS)
        other_sites_tokens_total = 0.0
        for site in data.other_sites:
            try:
                site_type = site.site_type.upper()
            except Exception:
                site_type = 'USD'
            if site_type == 'USD':
                other_sites_tokens_total += site.amount * self.token_to_usd_rate
            else:
                other_sites_tokens_total += site.amount

        total_tokens_all_sites = float(data.tokens) + other_sites_tokens_total

        # Calculate bonus based on total tokens across all sites
        # If disable_bonus flag is set, bonus_percentage will be 0
        if getattr(data, 'disable_bonus', False):
            bonus_percentage = 0.0
        else:
            bonus_percentage = self._calculate_bonus_percentage(total_tokens_all_sites)
        
        # Apply bonus to the original percentage
        original_percentage = data.percentage
        if original_percentage > 1:
            original_percentage = original_percentage / 100.0
        
        final_percentage = original_percentage + bonus_percentage

        # Dynamic TRM adjustment rule:
        # - Default adjustment: self.trm_adjustment (e.g., 300 COP)
        # - If total tokens >= 3000, reduce adjustment to 200 COP
        # - If override flag is set, always use default adjustment (ignore 3000+ rule)
        if getattr(data, 'override_high_tokens_trm', False):
            trm_adjustment_used = self.trm_adjustment
        else:
            trm_adjustment_used = 200 if total_tokens_all_sites >= 3000 else self.trm_adjustment
        trm_broadspec_cop = data.trm_official_cop - trm_adjustment_used
        
        transfer_cost_usd = self.transfer_cost + (self.transfer_cost * self.transfer_cost_tax)
        transfer_cost_cop = transfer_cost_usd * data.btk_trm_cop
        
        usd_from_tokens = data.tokens / self.token_to_usd_rate
        
        # Use final percentage (original + bonus) for calculations
        net_usd = usd_from_tokens * final_percentage

        # Other sites USD should be treated like tokens: convert to USD, then apply percentage.
        other_sites_total_usd_raw = sum(site.get_usd_equivalent() for site in data.other_sites)
        other_sites_total_usd = other_sites_total_usd_raw * final_percentage
        
        total_usd_precalc = net_usd + other_sites_total_usd + data.previous_fortnight_usd
        
        valor_broadspec_cop = (total_usd_precalc * trm_broadspec_cop) - transfer_cost_cop
        
        fines_total, fines_display, show_fines = self._calculate_fines(data)
        
        advances_total = sum(advance.amount for advance in data.advances)
        extras_total = sum(extra.amount for extra in data.extras)
        
        total_cop = valor_broadspec_cop - advances_total - fines_total + extras_total
        total_usd = total_cop / trm_broadspec_cop
        
        # Calculate bonus amounts in USD and COP
        bonus_amount_usd = (usd_from_tokens + other_sites_total_usd_raw) * bonus_percentage
        bonus_amount_cop = bonus_amount_usd * trm_broadspec_cop
        
        # Token value in COP (BTK TRM * 0.05) as per calculation notes
        token_value_cop = data.btk_trm_cop * 0.05
        
        # USD to send to platform:
        # ((Total COP + Transfer Cost COP) / token_value_cop) => tokens required
        # divide by token_to_usd_rate (tokens per USD) to get USD
        if token_value_cop <= 0 or self.token_to_usd_rate <= 0:
            usd_to_send_platform = 0.0
        else:
            usd_to_send_platform = ((total_cop + transfer_cost_cop) / token_value_cop) / self.token_to_usd_rate
        
        return CalculationResult(
            total_cop=total_cop,
            total_usd=total_usd,
            btk_trm_cop=data.btk_trm_cop,
            trm_broadspec_cop=trm_broadspec_cop,
            transfer_cost_cop=transfer_cost_cop,
            valor_broadspec_cop=valor_broadspec_cop,
            fines_total=fines_total,
            fines_display=fines_display,
            show_fines=show_fines,
            advances_total=advances_total,
            extras_total=extras_total,
            other_sites_total_usd=other_sites_total_usd,
            usd_from_tokens=usd_from_tokens,
            net_usd=net_usd,
            total_usd_precalc=total_usd_precalc,
            usd_to_send_platform=usd_to_send_platform,
            date=(getattr(data, 'date', "") or datetime.now().strftime("%Y-%m-%d")),
            total_tokens_all_sites=total_tokens_all_sites,
            bonus_percentage=bonus_percentage,
            bonus_amount_usd=bonus_amount_usd,
            bonus_amount_cop=bonus_amount_cop,
            original_percentage=original_percentage,
            final_percentage=final_percentage
        )
    
    def _calculate_bonus_percentage(self, total_tokens: float) -> float:
        """Calculate bonus percentage based on total tokens across all sites.
        
        Bonus thresholds:
        - 15,000+ tokens: 2.5%
        - 17,500+ tokens: 3.5%
        - 20,000+ tokens: 5.0%
        - 22,500+ tokens: 6.0%
        - 25,000+ tokens: 7.5%
        - 27,500+ tokens: 8.5%
        - 30,000+ tokens: 10.0%
        """
        if total_tokens >= 30000:
            return 0.10  # 10%
        elif total_tokens >= 27500:
            return 0.085  # 8.5%
        elif total_tokens >= 25000:
            return 0.075  # 7.5%
        elif total_tokens >= 22500:
            return 0.06  # 6.0%
        elif total_tokens >= 20000:
            return 0.05  # 5.0%
        elif total_tokens >= 17500:
            return 0.035  # 3.5%
        elif total_tokens >= 15000:
            return 0.025  # 2.5%
        else:
            return 0.0  # No bonus
    
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
        
        for i, extra in enumerate(data.extras):
            if extra.amount < 0:
                errors.append(f"Extra {i+1} amount cannot be negative")
        
        for i, site in enumerate(data.other_sites):
            if site.amount < 0:
                errors.append(f"Other Site {i+1} amount cannot be negative")
            if site.site_type not in ['USD', 'TKS']:
                errors.append(f"Other Site {i+1} type must be USD or TKS")
        
        return errors
