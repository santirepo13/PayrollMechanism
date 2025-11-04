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
    
    def __post_init__(self):
        if not self.other_sites:
            self.other_sites = []
        if not self.advances:
            self.advances = []


@dataclass
class CalculationResult:
    """Result of payment calculation."""
    total_cop: float
    total_usd: float
    trm_broadspec_cop: float
    transfer_cost_cop: float
    valor_broadspec_cop: float
    fines_total: float
    fines_display: str
    show_fines: bool
    advances_total: float
    other_sites_total_usd: float
    usd_from_tokens: float
    net_usd: float
    total_usd_precalc: float
    date: str
    
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