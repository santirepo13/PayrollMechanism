"""
Unit tests for receipt generator.
"""
import pytest
import re
import os
import tempfile
from unittest.mock import patch, MagicMock
 
from broadspec.core.receipt_generator import ReceiptGenerator
from broadspec.core.models import CalculationResult
from broadspec.core.exceptions import ReceiptGenerationError


class TestReceiptGenerator:
    """Test cases for ReceiptGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            'storage': {
                'receipts_path': tempfile.mkdtemp()
            }
        }
        self.generator = ReceiptGenerator(self.config)
        
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
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.config['storage']['receipts_path'], ignore_errors=True)
    
    def test_init_with_config(self):
        """Test initialization with configuration."""
        assert self.generator.receipts_path == self.config['storage']['receipts_path']
    
    def test_init_without_config(self):
        """Test initialization without configuration."""
        generator = ReceiptGenerator()
        assert generator.receipts_path == 'Receipts'
    
    def test_generate_pdf_success(self):
        """Test successful PDF generation."""
        pdf_path = self.generator.generate_pdf(self.test_input_data, self.test_result)
        
        assert os.path.exists(pdf_path)
        assert pdf_path.endswith('.pdf')
        assert os.path.getsize(pdf_path) > 0
        
        # Check filename format
        filename = os.path.basename(pdf_path)
        assert '12345' in filename
        assert 'Test Model' in filename
        assert '1000 TKS' in filename
        assert re.search(r'\d+\.\d{2,3}\sUSD', filename)
        assert '1.000.000 COP' in filename
        assert '2025-01-20' in filename
    
    def test_generate_pdf_creates_directory(self):
        """Test that PDF generation creates directory if it doesn't exist."""
        new_path = os.path.join(tempfile.mkdtemp(), 'new_receipts')
        config = {'storage': {'receipts_path': new_path}}
        generator = ReceiptGenerator(config)
        
        pdf_path = generator.generate_pdf(self.test_input_data, self.test_result)
        
        assert os.path.exists(new_path)
        assert os.path.exists(pdf_path)
        
        # Cleanup
        import shutil
        shutil.rmtree(new_path, ignore_errors=True)
    
    def test_generate_pdf_error_handling(self):
        """Test PDF generation error handling."""
        # Mock canvas.Canvas to raise an exception
        with patch('broadspec.core.receipt_generator.canvas.Canvas') as mock_canvas:
            mock_canvas.side_effect = Exception("PDF generation failed")
            
            with pytest.raises(ReceiptGenerationError) as exc_info:
                self.generator.generate_pdf(self.test_input_data, self.test_result)
            
            assert "Failed to generate PDF" in str(exc_info.value)
    
    def test_generate_filename(self):
        """Test filename generation."""
        from broadspec.utils.pdf_protocols import generate_filename
        filename = generate_filename(self.test_input_data, self.test_result)
        
        assert '12345' in filename
        assert 'Test Model' in filename
        assert '1000 TKS' in filename
        assert re.search(r'\d+\.\d{2,3}\sUSD', filename)
        assert '1.000.000 COP' in filename
        assert filename.endswith('.pdf')
    
    def test_format_other_sites_full(self):
        """Test formatting other sites for full receipt."""
        lines = self.generator._format_other_sites_full(self.test_input_data)
        
        assert len(lines) == 2
        assert "Site 2: $100.00 USD" in lines[0].strip()
        assert "Site 3: 200 TKS => $10.00 USD" in lines[1].strip()
    
    def test_format_other_sites_full_empty(self):
        """Test formatting empty other sites for full receipt."""
        data = self.test_input_data.copy()
        data['other_sites'] = []
        
        lines = self.generator._format_other_sites_full(data)
        
        assert len(lines) == 1
        assert lines[0] == "None"
    
    def test_format_other_sites_simple(self):
        """Test formatting other sites for simple receipt."""
        lines = self.generator._format_other_sites_simple(self.test_input_data)
        
        assert len(lines) == 2
        assert "Site 2: $100.00" in lines[0].strip()
        assert "Site 3: 200 TKS" in lines[1].strip()
    
    def test_format_advances_full(self):
        """Test formatting advances for full receipt."""
        lines = self.generator._format_advances_full(self.test_input_data)
        
        assert len(lines) == 3  # 2 advances + empty line
        assert "2025-01-01: $100,000.00 COP" in lines[0].strip()
        assert "2025-01-15: $50,000.00 COP" in lines[1].strip()
        assert lines[2] == ""
    
    def test_format_advances_full_empty(self):
        """Test formatting empty advances for full receipt."""
        data = self.test_input_data.copy()
        data['advances'] = []
        
        lines = self.generator._format_advances_full(data)
        
        assert len(lines) == 1
        assert lines[0] == "None\n"
    
    def test_format_advances_simple(self):
        """Test formatting advances for simple receipt."""
        lines = self.generator._format_advances_simple(self.test_input_data)
        
        assert len(lines) == 2
        assert "2025-01-01: $100,000" in lines[0].strip()
        assert "2025-01-15: $50,000" in lines[1].strip()
    
    def test_generate_full_receipt_lines(self):
        """Test generation of full receipt lines."""
        lines = self.generator._generate_full_receipt_lines(self.test_input_data, self.test_result)
        
        # Check that key information is present
        receipt_text = "\n".join(lines)
        assert "12345" in receipt_text
        assert "Test Model" in receipt_text
        assert "2025-01-20" in receipt_text
        assert "$4,000.00" in receipt_text  # TRM Official
        assert "$3,700.00" in receipt_text  # TRM BroadSpec
        assert "1,000" in receipt_text  # Tokens
        assert "70%" in receipt_text  # Percentage
        assert "$100.00 USD" in receipt_text  # Other site USD
        assert "200 TKS" in receipt_text  # Other site TKS
        assert "$100,000.00 COP" in receipt_text  # Advance
        assert "2 fines x 30,000" in receipt_text  # Fines
        assert "$1,000,000.00 COP" in receipt_text  # Total payment
    
    def test_generate_simple_receipt_lines(self):
        """Test generation of simple receipt lines."""
        lines = self.generator._generate_simple_receipt_lines(self.test_input_data, self.test_result)
        
        # Check that key information is present
        receipt_text = "\n".join(lines)
        assert "12345" in receipt_text
        assert "Test Model" in receipt_text
        assert "2025-01-20" in receipt_text
        assert "$4,000.00 COP" in receipt_text  # TRM Official
        assert "$3,700.00 COP" in receipt_text  # TRM BroadSpec
        assert "1,000" in receipt_text  # Tokens
        assert "70%" in receipt_text  # Percentage
        assert "$100.00" in receipt_text  # Other site USD
        assert "200 TKS" in receipt_text  # Other site TKS
        assert "$100,000" in receipt_text  # Advance (no decimals)
        assert "$1,000,000.00 COP" in receipt_text  # Total payment
    
    def test_simple_receipt_without_fines(self):
        """Test simple receipt generation when fines are disabled."""
        # Modify result to disable fines
        self.test_result.show_fines = False
        
        lines = self.generator._generate_simple_receipt_lines(self.test_input_data, self.test_result)
        receipt_text = "\n".join(lines)
        
        # Fines section should not be present
        assert "Fines:" not in receipt_text
        assert "$60,000" not in receipt_text