from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Advance:
    """Represents an advance payment with date and amount."""
    date: str
    amount: float
    
    def __post_init__(self):
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d")


@dataclass
class OtherSite:
    """Represents payment from other sites."""
    site_type: str
    amount: float
    
    def get_usd_equivalent(self) -> float:
        """Convert to USD equivalent."""
        if self.site_type.upper() == 'USD':
            return self.amount
        else:
            return self.amount / 20.0


@dataclass
class PaymentData:
    """Contains all payment calculation data."""
    model_id: str
    model_name: str
    trm_official_cop: float
    btk_trm_cop: float
    tokens: int
    percentage: float
    previous_fortnight_usd: float
    other_sites: List[OtherSite]
    advances: List[Advance]
    fines_count: int
    custom_fine_cop: float
    # If True, always use the standard TRM adjustment (e.g., -300),
    # ignoring the 3000+ tokens rule that reduces the adjustment to -200.
    override_high_tokens_trm: bool = False
    
    def __post_init__(self):
        if not self.other_sites:
            self.other_sites = []
        if not self.advances:
            self.advances = []


@dataclass
class CalculationResult:
    """Result of payment calculation."""
    total_cop: float = 0.0
    total_usd: float = 0.0
    trm_broadspec_cop: float = 0.0
    transfer_cost_cop: float = 0.0
    valor_broadspec_cop: float = 0.0
    fines_total: float = 0.0
    fines_display: str = ""
    show_fines: bool = True
    advances_total: float = 0.0
    other_sites_total_usd: float = 0.0
    usd_from_tokens: float = 0.0
    net_usd: float = 0.0
    total_usd_precalc: float = 0.0
    usd_to_send_platform: float = 0.0
    btk_trm_cop: float = 0.0
    date: str = ""
    
    def __init__(self, *args, **kwargs):
        """
        Flexible constructor to remain backward-compatible with older positional
        usages while preferring keyword arguments. Fields are accepted in the
        legacy positional order if used.
        """
        defaults = {
            'total_cop': 0.0, 'total_usd': 0.0, 'trm_broadspec_cop': 0.0,
            'transfer_cost_cop': 0.0, 'valor_broadspec_cop': 0.0,
            'fines_total': 0.0, 'fines_display': "", 'show_fines': True,
            'advances_total': 0.0, 'other_sites_total_usd': 0.0,
            'usd_from_tokens': 0.0, 'net_usd': 0.0, 'total_usd_precalc': 0.0,
            'usd_to_send_platform': 0.0, 'btk_trm_cop': 0.0, 'date': ""
        }
        field_order = [
            'total_cop', 'total_usd', 'trm_broadspec_cop', 'transfer_cost_cop',
            'valor_broadspec_cop', 'fines_total', 'fines_display', 'show_fines',
            'advances_total', 'other_sites_total_usd', 'usd_from_tokens',
            'net_usd', 'total_usd_precalc', 'usd_to_send_platform',
            'btk_trm_cop', 'date'
        ]
        # Assign from positional args first
        for i, name in enumerate(field_order):
            if i < len(args):
                value = args[i]
            else:
                value = kwargs.get(name, defaults[name])
            setattr(self, name, value)
    
    def __post_init__(self):
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d")


@dataclass
class VaultEntry:
    """Represents an entry in encrypted vault."""
    vault_filename: str
    orig_filename: str
    model_id: str
    model_name: str
    tokens: str
    date: str
    saved_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.saved_at:
            self.saved_at = datetime.now().isoformat()
