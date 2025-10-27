"""
Unit tests for PDF protocols module.
"""
import pytest
from datetime import datetime

from broadspec.utils.pdf_protocols import generate_filename, sanitize_filename
from broadspec.core.models import CalculationResult


class TestPDFProtocols:
    """Test cases for PDF protocols."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Sample test data
        self.test_input_data = {
            'model_id': '12345',
            'model_name': 'Test Model',
            'trm_official_cop': 4000,
            'tokens': 1000,
            'percentage': 0.7,
            'previous_fortnight_usd': 0,
            'other_sites': [
                {'site_type': 'USD', 'amount': 100},
                {'site_type': 'TKS', 'amount': 200}
            ],
            'advances': [
                {'date': '2025-01-01', 'amount': 100000},
                {'date': '2025-01-15', 'amount': 50000}
            ],
            'fines_count': 2,
            'custom_fine_cop': 0
        }
        
        self.test_result = CalculationResult(
            total_cop=1000000,
            total_usd=250,
            trm_broadspec_cop=3700,
            transfer_cost_cop=30000,
            valor_broadspec_cop=1080000,
            fines_total=60000,
            fines_display="2 fines x 30,000 = 60,000 COP",
            show_fines=True,
            advances_total=150000,
            other_sites_total_usd=110,
            usd_from_tokens=50,
            net_usd=35,
            total_usd_precalc=145,
            date='2025-01-20'
        )
    
    def test_generate_filename_with_result(self):
        """Test filename generation with result."""
        filename = generate_filename(self.test_input_data, self.test_result)
        
        assert '12345' in filename
        assert 'Test Model' in filename
        assert '1000 TKS' in filename
        assert '250.00 USD' in filename
        assert '1.000.000 COP' in filename
        assert datetime.now().strftime("%Y-%m-%d") in filename
        assert filename.endswith('.pdf')
    
    def test_generate_filename_without_result(self):
        """Test filename generation without result."""
        filename = generate_filename(self.test_input_data)
        
        assert '12345' in filename
        assert 'Test Model' in filename
        assert '1000 TKS' in filename
        assert ' USD' in filename  # Empty USD amount
        assert ' COP' in filename  # Empty COP amount
        assert datetime.now().strftime("%Y-%m-%d") in filename
        assert filename.endswith('.pdf')
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test with invalid characters
        invalid_name = "Test<>:\"/\\|?*Model"
        sanitized = sanitize_filename(invalid_name)
        assert sanitized == "Test_________Model"
        
        # Test with trailing spaces and dots
        trailing_name = "Test Model   ... "
        sanitized = sanitize_filename(trailing_name)
        assert sanitized == "Test Model"
        
        # Test with empty name
        sanitized = sanitize_filename("")
        assert sanitized == "unnamed"