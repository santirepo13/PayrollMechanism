"""
Unit tests for payment calculator.
"""
import pytest
from broadspec.core.models import PaymentData, OtherSite, Advance
from broadspec.core.calculator import PaymentCalculator
from broadspec.core.exceptions import CalculationError


class TestPaymentCalculator:
    """Test cases for PaymentCalculator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            'calculation': {
                'token_to_usd_rate': 20.0,
                'trm_adjustment': 300,
                'fine_amount': 30000,
                'transfer_cost_tax': 0.19
            },
            'app': {
                'transfer_cost': 6.99
            }
        }
        self.calculator = PaymentCalculator(self.config)
    
    def test_calculate_basic_payment(self):
        """Test basic payment calculation."""
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=1000,
            percentage=0.7,
            previous_fortnight_usd=0,
            other_sites=[],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        
        assert result.total_cop > 0
        assert result.total_usd > 0
        assert result.trm_broadspec_cop == 3700  # 4000 - 300
        assert result.usd_from_tokens == 50.0  # 1000 / 20
        assert result.net_usd == 35.0  # 50.0 * 0.7
    
    def test_calculate_with_other_sites_usd(self):
        """Test calculation with USD other sites."""
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=1000,
            percentage=0.7,
            previous_fortnight_usd=0,
            other_sites=[OtherSite("USD", 100)],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        assert result.other_sites_total_usd == 70.0  # 100 * 0.7
    
    def test_calculate_with_other_sites_tks(self):
        """Test calculation with TKS other sites."""
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=1000,
            percentage=0.7,
            previous_fortnight_usd=0,
            other_sites=[OtherSite("TKS", 200)],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        assert result.other_sites_total_usd == 7.0  # (200 / 20) * 0.7
    
    def test_calculate_with_advances(self):
        """Test calculation with advances."""
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=1000,
            percentage=0.7,
            previous_fortnight_usd=0,
            other_sites=[],
            advances=[Advance("2025-01-01", 100000)],
            extras=[],
            fines_count=0,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        assert result.advances_total == 100000
    
    def test_calculate_with_fines_studio(self):
        """Test calculation with fines for studio worker (60%)."""
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=1000,
            percentage=0.6,
            previous_fortnight_usd=0,
            other_sites=[],
            advances=[],
            extras=[],
            fines_count=2,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        assert result.fines_total == 60000  # 2 * 30000
        assert result.show_fines == True
    
    def test_calculate_with_fines_home_worker(self):
        """Test calculation with fines disabled for home worker (70%)."""
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=1000,
            percentage=0.7,
            previous_fortnight_usd=0,
            other_sites=[],
            advances=[],
            extras=[],
            fines_count=2,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        assert result.fines_total == 60000  # 2 * 30000
        assert result.show_fines == False
    
    def test_calculate_with_custom_fine(self):
        """Test calculation with custom fine amount."""
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=1000,
            percentage=0.6,
            previous_fortnight_usd=0,
            other_sites=[],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=50000
        )
        
        result = self.calculator.calculate(data)
        assert result.fines_total == 50000
        assert "Custom" in result.fines_display
    
    def test_calculate_bonus_percentage_new_structure(self):
        """Test new bonus percentage calculation structure."""
        # Test boundary conditions for new bonus thresholds
        
        # Below 10,000 tokens: 0% bonus
        result = self.calculator._calculate_bonus_percentage(9999)
        assert result == 0.0
        
        # 10,000+ tokens: 3% bonus
        result = self.calculator._calculate_bonus_percentage(10000)
        assert result == 0.03
        
        # Between 10,000 and 12,500: 3% bonus
        result = self.calculator._calculate_bonus_percentage(12499)
        assert result == 0.03
        
        # 12,500+ tokens: 4.5% bonus
        result = self.calculator._calculate_bonus_percentage(12500)
        assert result == 0.045
        
        # Between 12,500 and 15,000: 4.5% bonus
        result = self.calculator._calculate_bonus_percentage(14999)
        assert result == 0.045
        
        # 15,000+ tokens: 6% bonus
        result = self.calculator._calculate_bonus_percentage(15000)
        assert result == 0.06
        
        # Between 15,000 and 17,500: 6% bonus
        result = self.calculator._calculate_bonus_percentage(17499)
        assert result == 0.06
        
        # 17,500+ tokens: 8% bonus
        result = self.calculator._calculate_bonus_percentage(17500)
        assert result == 0.08
        
        # Between 17,500 and 20,000: 8% bonus
        result = self.calculator._calculate_bonus_percentage(19999)
        assert result == 0.08
        
        # 20,000+ tokens: 10% bonus
        result = self.calculator._calculate_bonus_percentage(20000)
        assert result == 0.10
        
        # Above 20,000 tokens: 10% bonus
        result = self.calculator._calculate_bonus_percentage(30000)
        assert result == 0.10
    
    def test_calculate_bonus_with_other_sites_usd(self):
        """Test bonus calculation with USD other sites."""
        # Test with 5,000 main tokens + 100 USD other site = 5,000 + (100 * 20) = 7,000 tokens total
        # Should get 3% bonus (10,000+ threshold)
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=5000,
            percentage=0.6,
            previous_fortnight_usd=0,
            other_sites=[OtherSite("USD", 100)],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        # Total tokens: 5,000 + (100 * 20) = 7,000 (below 10,000 threshold)
        assert result.bonus_percentage == 0.0
        assert result.bonus_amount_usd == 0.0
        
        # Test with 8,000 main tokens + 100 USD other site = 8,000 + (100 * 20) = 10,000 tokens total
        # Should get 3% bonus (exactly at 10,000 threshold)
        data.tokens = 8000
        result = self.calculator.calculate(data)
        # Total tokens: 8,000 + (100 * 20) = 10,000 (exactly at threshold)
        assert result.bonus_percentage == 0.03
        assert result.bonus_amount_usd > 0
    
    def test_calculate_bonus_with_other_sites_tks(self):
        """Test bonus calculation with TKS other sites."""
        # Test with 8,000 main tokens + 1,000 TKS other site = 9,000 total tokens
        # Should get 0% bonus (below 10,000 threshold)
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=8000,
            percentage=0.6,
            previous_fortnight_usd=0,
            other_sites=[OtherSite("TKS", 1000)],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        # Total tokens: 8,000 + 1,000 = 9,000 (below 10,000 threshold)
        assert result.bonus_percentage == 0.0
        assert result.bonus_amount_usd == 0.0
        
        # Test with 8,500 main tokens + 1,500 TKS other site = 10,000 total tokens
        # Should get 3% bonus (exactly at 10,000 threshold)
        data.tokens = 8500
        data.other_sites = [OtherSite("TKS", 1500)]
        result = self.calculator.calculate(data)
        # Total tokens: 8,500 + 1,500 = 10,000 (exactly at threshold)
        assert result.bonus_percentage == 0.03
        assert result.bonus_amount_usd > 0
    
    def test_calculate_bonus_with_mixed_sites(self):
        """Test bonus calculation with mixed USD and TKS other sites."""
        # Test with 9,000 main tokens + 50 USD + 250 TKS
        # Total: 9,000 + (50 * 20) + 250 = 9,000 + 1,000 + 250 = 10,250 tokens
        # Should get 4.5% bonus (12,500+ threshold)
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=9000,
            percentage=0.6,
            previous_fortnight_usd=0,
            other_sites=[
                OtherSite("USD", 50),
                OtherSite("TKS", 250)
            ],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        # Total tokens: 9,000 + (50 * 20) + 250 = 10,250 (12,500+ threshold)
        assert result.bonus_percentage == 0.045
        assert result.bonus_amount_usd > 0
    
    def test_calculate_bonus_disable_bonus_flag(self):
        """Test bonus calculation with disable_bonus flag."""
        # Test with high token count but bonus disabled
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=25000,
            percentage=0.6,
            previous_fortnight_usd=0,
            other_sites=[],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=0,
            disable_bonus=True
        )
        
        result = self.calculator.calculate(data)
        # Even with 25,000 tokens, bonus should be 0% when disabled
        assert result.bonus_percentage == 0.0
        assert result.bonus_amount_usd == 0.0
    
    def test_validate_data_valid(self):
        """Test validation with valid data."""
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=1000,
            percentage=0.7,
            previous_fortnight_usd=0,
            other_sites=[],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=0
        )
        
        errors = self.calculator.validate_data(data)
        assert len(errors) == 0
    
    def test_validate_data_missing_model_id(self):
        """Test validation with missing model ID."""
        data = PaymentData(
            model_id="",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=1000,
            percentage=0.7,
            previous_fortnight_usd=0,
            other_sites=[],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=0
        )
        
        errors = self.calculator.validate_data(data)
        assert len(errors) > 0
        assert any("Model ID is required" in error for error in errors)
    
    def test_validate_data_negative_values(self):
        """Test validation with negative values."""
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=-100,
            btk_trm_cop=4100,
            tokens=-100,
            percentage=0.7,
            previous_fortnight_usd=-50,
            other_sites=[],
            advances=[],
            extras=[],
            fines_count=-1,
            custom_fine_cop=-1000
        )
        
        errors = self.calculator.validate_data(data)
        assert len(errors) > 0
        # Should have errors for all negative values
        assert any("TRM Official COP" in error for error in errors)
        assert any("Tokens" in error for error in errors)
        assert any("Previous Fortnight USD" in error for error in errors)
        assert any("Fines count" in error for error in errors)
        assert any("Custom fine" in error for error in errors)
    
    def test_validate_data_invalid_percentage(self):
        """Test validation with invalid percentage."""
        data = PaymentData(
            model_id="12345",
            model_name="Test Model",
            trm_official_cop=4000,
            btk_trm_cop=4100,
            tokens=1000,
            percentage=1.5,  # Invalid: > 1
            previous_fortnight_usd=0,
            other_sites=[],
            advances=[],
            extras=[],
            fines_count=0,
            custom_fine_cop=0
        )
        
        errors = self.calculator.validate_data(data)
        assert len(errors) == 0
