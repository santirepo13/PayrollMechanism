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
            fines_count=0,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        assert result.other_sites_total_usd == 100.0
    
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
            fines_count=0,
            custom_fine_cop=0
        )
        
        result = self.calculator.calculate(data)
        assert result.other_sites_total_usd == 10.0  # 200 / 20
    
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
            fines_count=0,
            custom_fine_cop=50000
        )
        
        result = self.calculator.calculate(data)
        assert result.fines_total == 50000
        assert "Custom" in result.fines_display
    
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
            fines_count=0,
            custom_fine_cop=0
        )
        
        errors = self.calculator.validate_data(data)
        assert len(errors) == 0
