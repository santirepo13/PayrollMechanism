"""
Main entry point for BroadSpec Payment Calculator.
"""
import os
import sys
# Ensure repository root is on sys.path so package imports work when running this file directly.
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import tkinter as tk
from tkinter import messagebox
import yaml
from datetime import datetime

from core.calculator import PaymentCalculator
from core.receipt_generator import ReceiptGenerator
from core.models import PaymentData, OtherSite, Advance, CalculationResult
from storage.vault_manager import VaultRepository
from storage.file_operations import FileOperations
from ui.main_window import BroadSpecGUI
from core.exceptions import BroadSpecError, CalculationError, ValidationError, ReceiptGenerationError, ConfigurationError, VaultError
from utils.validators import validate_payment_data
from utils.formatters import format_currency_cop, format_currency_usd


class ApplicationController:
    """Main application controller implementing MVC pattern."""
    
    def __init__(self):
        """Initialize the application controller."""
        self.config = {}
        self.calculator = None
        self.receipt_generator = None
        self.vault_repository = None
        self.file_operations = None
        self.gui = None
        self.root = None
        
        # Initialize application
        self._load_configuration()
        self._initialize_components()
    
    def _load_configuration(self):
        """Load application configuration."""
        try:
            config_path = 'config.yaml'
            if not os.path.exists(config_path):
                raise ConfigurationError(f"Configuration file not found: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
                
        except Exception as e:
            error_msg = f"Failed to load configuration: {str(e)}"
            if hasattr(self, 'root') and self.root:
                messagebox.showerror("Configuration Error", error_msg)
            else:
                print(f"ERROR: {error_msg}")
            sys.exit(1)
    
    def _initialize_components(self):
        """Initialize application components."""
        try:
            # Initialize core components
            self.calculator = PaymentCalculator(self.config)
            self.receipt_generator = ReceiptGenerator(self.config)
            self.file_operations = FileOperations(self.config)
            
            # Initialize vault repository (may fail if cryptography not available)
            try:
                self.vault_repository = VaultRepository(self.config)
                self.vault_repository.load_index()
            except (ConfigurationError, VaultError) as e:
                print(f"Warning: Vault features disabled: {str(e)}")
                self.vault_repository = None
                
        except Exception as e:
            error_msg = f"Failed to initialize components: {str(e)}"
            if hasattr(self, 'root') and self.root:
                messagebox.showerror("Initialization Error", error_msg)
            else:
                print(f"ERROR: {error_msg}")
            sys.exit(1)
    
    def initialize_gui(self, root: tk.Tk):
        """Initialize the GUI."""
        try:
            self.root = root
            self.gui = BroadSpecGUI(root, self.config, self)
            
        except Exception as e:
            error_msg = f"Failed to initialize GUI: {str(e)}"
            messagebox.showerror("GUI Error", error_msg)
            sys.exit(1)
    
    def calculate_payment(self, form_data: dict) -> tuple[dict, dict]:
        """
        Calculate payment based on form data.
        
        Args:
            form_data: Dictionary containing form input values
            
        Returns:
            Tuple of (input_data, calculation_result)
            
        Raises:
            BroadSpecError: If calculation fails
        """
        try:
            # Convert form data to PaymentData model
            payment_data = self._form_data_to_payment_data(form_data)
            
            # Validate input data
            validation_errors = self.calculator.validate_data(payment_data)
            if validation_errors:
                raise ValidationError("Validation failed: " + "; ".join(validation_errors))
            
            # Perform calculation
            result = self.calculator.calculate(payment_data)
            
            # Convert to dictionaries for GUI
            input_dict = self._payment_data_to_dict(payment_data)
            result_dict = self._calculation_result_to_dict(result)
            
            return input_dict, result_dict
            
        except Exception as e:
            if isinstance(e, BroadSpecError):
                raise
            raise CalculationError(f"Payment calculation failed: {str(e)}")
    
    def save_receipt(self, input_data: dict, result_data: dict) -> str:
        """
        Save receipt as PDF and optionally add to vault.
        
        Args:
            input_data: Input data dictionary
            result_data: Calculation result dictionary
            
        Returns:
            Path to the saved PDF file
            
        Raises:
            BroadSpecError: If save operation fails
        """
        try:
            # Convert back to model objects
            payment_data = self._dict_to_payment_data(input_data)
            result = self._dict_to_calculation_result(result_data)
            
            # Generate PDF
            pdf_path = self.receipt_generator.generate_pdf(input_data, result)
            
            # Add to vault if available and not a test entry
            if (self.vault_repository and 
                not (input_data.get('model_id') == "000" and 
                     input_data.get('model_name', '').lower() == "test")):
                
                try:
                    metadata = {
                        'model_id': input_data.get('model_id'),
                        'model_name': input_data.get('model_name'),
                        'tokens': input_data.get('tokens'),
                        'date': result.date
                    }
                    self.vault_repository.add_file(pdf_path, metadata)
                except Exception as e:
                    # Don't fail the save operation if vault add fails
                    print(f"Warning: Failed to add to vault: {str(e)}")
            
            return pdf_path
            
        except Exception as e:
            if isinstance(e, BroadSpecError):
                raise
            raise ReceiptGenerationError(f"Failed to save receipt: {str(e)}")
    
    def get_vault_entries(self) -> list[dict]:
        """Get all vault entries."""
        if not self.vault_repository:
            return []
        
        try:
            return self.vault_repository.get_all_entries()
        except Exception as e:
            print(f"Error getting vault entries: {str(e)}")
            return []
    
    def export_from_vault(self, vault_filename: str, export_path: str = None) -> str:
        """
        Export a file from the vault.
        
        Args:
            vault_filename: Filename in vault
            export_path: Optional export path
            
        Returns:
            Path to the exported file
            
        Raises:
            BroadSpecError: If export fails
        """
        if not self.vault_repository:
            raise VaultError("Vault not available")
        
        try:
            # Retrieve file from vault
            file_bytes = self.vault_repository.retrieve_file(vault_filename)
            
            # Determine export path
            if not export_path:
                export_path = self.file_operations.get_unique_filepath(
                    self.file_operations.ensure_receipts_directory(),
                    vault_filename
                )
            
            # Save file
            self.file_operations.save_file(export_path, file_bytes)
            
            return export_path
            
        except Exception as e:
            if isinstance(e, BroadSpecError):
                raise
            raise VaultError(f"Failed to export from vault: {str(e)}")
    
    def delete_from_vault(self, vault_filenames: list[str]) -> int:
        """
        Delete files from the vault.
        
        Args:
            vault_filenames: List of filenames to delete
            
        Returns:
            Number of files deleted
            
        Raises:
            BroadSpecError: If deletion fails
        """
        if not self.vault_repository:
            raise VaultError("Vault not available")
        
        try:
            return self.vault_repository.delete_files(vault_filenames)
        except Exception as e:
            if isinstance(e, BroadSpecError):
                raise
            raise VaultError(f"Failed to delete from vault: {str(e)}")
    
    def import_to_vault(self, file_paths: list[str]) -> tuple[int, int]:
        """
        Import files to the vault.
        
        Args:
            file_paths: List of file paths to import
            
        Returns:
            Tuple of (success_count, failure_count)
        """
        if not self.vault_repository:
            raise VaultError("Vault not available")
        
        success_count = 0
        failure_count = 0
        
        for file_path in file_paths:
            try:
                # Extract basic metadata from filename
                filename = os.path.basename(file_path)
                metadata = {
                    'model_id': '',
                    'model_name': '',
                    'tokens': '',
                    'date': datetime.now().strftime("%Y-%m-%d")
                }
                
                self.vault_repository.add_file(file_path, metadata)
                success_count += 1
                
            except Exception:
                failure_count += 1
        
        return success_count, failure_count
    
    def get_vault_stats(self) -> dict:
        """Get vault statistics."""
        if not self.vault_repository:
            return {'count': 0, 'size': 0}
        
        try:
            entries = self.vault_repository.get_all_entries()
            size = self.vault_repository.get_vault_size()
            
            return {
                'count': len(entries),
                'size': size
            }
        except Exception:
            return {'count': 0, 'size': 0}
    
    # Helper methods for data conversion
    
    def _form_data_to_payment_data(self, form_data: dict) -> PaymentData:
        """Convert form data to PaymentData model."""
        # Convert other sites
        other_sites = []
        for site in form_data.get('other_sites', []):
            other_sites.append(OtherSite(
                site_type=site.get('site_type', 'USD'),
                amount=site.get('amount', 0)
            ))
        
        # Convert advances
        advances = []
        for advance in form_data.get('advances', []):
            advances.append(Advance(
                date=advance.get('date', ''),
                amount=advance.get('amount', 0)
            ))
        
        return PaymentData(
            model_id=form_data.get('model_id', ''),
            model_name=form_data.get('model_name', ''),
            trm_official_cop=form_data.get('trm_official_cop', 0),
            btk_trm_cop=form_data.get('btk_trm_cop', 0),
            tokens=form_data.get('tokens', 0),
            percentage=form_data.get('percentage', 0),
            previous_fortnight_usd=form_data.get('previous_fortnight_usd', 0),
            other_sites=other_sites,
            advances=advances,
            fines_count=form_data.get('fines_count', 0),
            custom_fine_cop=form_data.get('custom_fine_cop', 0)
        )
    
    def _payment_data_to_dict(self, data: PaymentData) -> dict:
        """Convert PaymentData to dictionary."""
        return {
            'model_id': data.model_id,
            'model_name': data.model_name,
            'trm_official_cop': data.trm_official_cop,
            'btk_trm_cop': data.btk_trm_cop,
            'tokens': data.tokens,
            'percentage': data.percentage,
            'previous_fortnight_usd': data.previous_fortnight_usd,
            'other_sites': [
                {'site_type': site.site_type, 'amount': site.amount}
                for site in data.other_sites
            ],
            'advances': [
                {'date': advance.date, 'amount': advance.amount}
                for advance in data.advances
            ],
            'fines_count': data.fines_count,
            'custom_fine_cop': data.custom_fine_cop
        }
    
    def _dict_to_payment_data(self, data_dict: dict) -> PaymentData:
        """Convert dictionary to PaymentData."""
        other_sites = [
            OtherSite(site['site_type'], site['amount'])
            for site in data_dict.get('other_sites', [])
        ]
        
        advances = [
            Advance(advance['date'], advance['amount'])
            for advance in data_dict.get('advances', [])
        ]
        
        return PaymentData(
            model_id=data_dict.get('model_id', ''),
            model_name=data_dict.get('model_name', ''),
            trm_official_cop=data_dict.get('trm_official_cop', 0),
            btk_trm_cop=data_dict.get('btk_trm_cop', 0),
            tokens=data_dict.get('tokens', 0),
            percentage=data_dict.get('percentage', 0),
            previous_fortnight_usd=data_dict.get('previous_fortnight_usd', 0),
            other_sites=other_sites,
            advances=advances,
            fines_count=data_dict.get('fines_count', 0),
            custom_fine_cop=data_dict.get('custom_fine_cop', 0)
        )
    
    def _calculation_result_to_dict(self, result: CalculationResult) -> dict:
        """Convert CalculationResult to dictionary."""
        return {
            'total_cop': result.total_cop,
            'total_usd': result.total_usd,
            'trm_broadspec_cop': result.trm_broadspec_cop,
            'transfer_cost_cop': result.transfer_cost_cop,
            'valor_broadspec_cop': result.valor_broadspec_cop,
            'fines_total': result.fines_total,
            'fines_display': result.fines_display,
            'show_fines': result.show_fines,
            'advances_total': result.advances_total,
            'other_sites_total_usd': result.other_sites_total_usd,
            'usd_from_tokens': result.usd_from_tokens,
            'net_usd': result.net_usd,
            'total_usd_precalc': result.total_usd_precalc,
            'date': result.date
        }
    
    def _dict_to_calculation_result(self, result_dict: dict) -> CalculationResult:
        """Convert dictionary to CalculationResult."""
        return CalculationResult(
            total_cop=result_dict.get('total_cop', 0),
            total_usd=result_dict.get('total_usd', 0),
            trm_broadspec_cop=result_dict.get('trm_broadspec_cop', 0),
            transfer_cost_cop=result_dict.get('transfer_cost_cop', 0),
            valor_broadspec_cop=result_dict.get('valor_broadspec_cop', 0),
            fines_total=result_dict.get('fines_total', 0),
            fines_display=result_dict.get('fines_display', ''),
            show_fines=result_dict.get('show_fines', False),
            advances_total=result_dict.get('advances_total', 0),
            other_sites_total_usd=result_dict.get('other_sites_total_usd', 0),
            usd_from_tokens=result_dict.get('usd_from_tokens', 0),
            net_usd=result_dict.get('net_usd', 0),
            total_usd_precalc=result_dict.get('total_usd_precalc', 0),
            date=result_dict.get('date', '')
        )


def main():
    """Main entry point."""
    try:
        # Create application controller
        app = ApplicationController()
        
        # Create and initialize GUI
        root = tk.Tk()
        app.initialize_gui(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Application failed to start: {str(e)}"
        print(f"ERROR: {error_msg}")
        if 'root' in locals():
            messagebox.showerror("Application Error", error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
