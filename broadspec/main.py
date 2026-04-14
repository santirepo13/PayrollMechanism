import os
import sys
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import tkinter as tk
from tkinter import messagebox
import yaml
from datetime import datetime

from broadspec.core.calculator import PaymentCalculator
from broadspec.core.receipt_generator import ReceiptGenerator
from broadspec.core.models import PaymentData, OtherSite, Advance, CalculationResult
from broadspec.storage.vault_manager import VaultRepository
from broadspec.storage.file_operations import FileOperations
from broadspec.ui.main_window import BroadSpecGUI
from broadspec.core.exceptions import BroadSpecError, CalculationError, ValidationError, ReceiptGenerationError, ConfigurationError, VaultError
from broadspec.utils.validators import validate_payment_data
from broadspec.utils.formatters import format_currency_cop, format_currency_usd
from broadspec.utils.pdf_protocols import generate_filename


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
        
        self._load_configuration()
        self._initialize_components()
    
    def _load_configuration(self):
        """Load application configuration."""
        try:
            config_path = os.path.join(_repo_root, 'config.yaml')
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
            self.calculator = PaymentCalculator(self.config)
            self.receipt_generator = ReceiptGenerator(self.config)
            self.file_operations = FileOperations(self.config)
            
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
        """Calculate payment based on form data."""
        try:
            payment_data = self._form_data_to_payment_data(form_data)
            
            validation_errors = self.calculator.validate_data(payment_data)
            if validation_errors:
                raise ValidationError("Validation failed: " + "; ".join(validation_errors))
            
            result = self.calculator.calculate(payment_data)
            
            input_dict = self._payment_data_to_dict(payment_data)
            result_dict = self._calculation_result_to_dict(result)
            
            # Ensure BTK TRM (btk_trm_cop) is available in the result payload
            # so UI and downstream consumers can reference the exact BTK TRM used.
            result_dict['btk_trm_cop'] = payment_data.btk_trm_cop
            
            return input_dict, result_dict
            
        except Exception as e:
            if isinstance(e, BroadSpecError):
                raise
            raise CalculationError(f"Payment calculation failed: {str(e)}")
    
    def save_receipt(self, input_data: dict, result_data: dict) -> str:
        """Save receipt directly into the encrypted vault (no local file)."""
        try:
            payment_data = self._dict_to_payment_data(input_data)
            result = self._dict_to_calculation_result(result_data)
            
            # Generate PDF in-memory (bytes) and add to vault without creating local file
            pdf_bytes = self.receipt_generator.generate_pdf_bytes(input_data, result)
            
            # Build a filename following existing protocol
            try:
                filename = generate_filename(input_data, result)
            except Exception:
                model_id = (input_data.get('model_id') or "").strip()
                model_name = (input_data.get('model_name') or "").strip()
                date_str = (result.date or "")
                filename = f"{model_id} - {model_name} - {date_str}.pdf"
            
            # Ensure vault is available
            if not self.vault_repository:
                raise VaultError("Vault not available")
            
            # Prepare metadata for vault index
            metadata = {
                'model_id': input_data.get('model_id'),
                'model_name': input_data.get('model_name'),
                'tokens': input_data.get('tokens'),
                'date': result.date
            }
            
            # Add PDF bytes directly to vault (no local file)
            try:
                entry = self.vault_repository.add_bytes(pdf_bytes, filename, metadata)
            except Exception as e:
                raise VaultError(f"Failed to add PDF to vault: {str(e)}")
            
            # Return vault filename (not a local path)
            return entry.vault_filename
            
        except Exception as e:
            if isinstance(e, BroadSpecError):
                raise
            raise ReceiptGenerationError(f"Failed to save receipt: {str(e)}")
    
    def generate_receipt_pdf(self, input_data: dict, result_data: dict, pdf_path: str):
        """Generate PDF receipt to specified path."""
        try:
            payment_data = self._dict_to_payment_data(input_data)
            result = self._dict_to_calculation_result(result_data)
            
            self.receipt_generator.generate_pdf_to_path(payment_data, result, pdf_path)
            
        except Exception as e:
            if isinstance(e, BroadSpecError):
                raise
            raise ReceiptGenerationError(f"Failed to generate PDF: {str(e)}")
    
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
        """Export a file from the vault."""
        if not self.vault_repository:
            raise VaultError("Vault not available")
        
        try:
            file_bytes = self.vault_repository.retrieve_file(vault_filename)
            
            if not export_path:
                export_path = self.file_operations.get_unique_filepath(
                    self.file_operations.ensure_receipts_directory(),
                    vault_filename
                )
            
            self.file_operations.save_file(export_path, file_bytes)
            
            return export_path
            
        except Exception as e:
            if isinstance(e, BroadSpecError):
                raise
            raise VaultError(f"Failed to export from vault: {str(e)}")
    
    def delete_from_vault(self, vault_filenames: list[str]) -> int:
        """Delete files from the vault."""
        if not self.vault_repository:
            raise VaultError("Vault not available")
        
        try:
            return self.vault_repository.delete_files(vault_filenames)
        except Exception as e:
            if isinstance(e, BroadSpecError):
                raise
            raise VaultError(f"Failed to delete from vault: {str(e)}")
    
    def import_to_vault(self, file_paths: list[str]) -> tuple[int, int]:
        """Import files to the vault."""
        if not self.vault_repository:
            raise VaultError("Vault not available")
        
        success_count = 0
        failure_count = 0
        
        for file_path in file_paths:
            try:
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
    
    def _form_data_to_payment_data(self, form_data: dict) -> PaymentData:
        """Convert form data to PaymentData model."""
        other_sites = []
        for site in form_data.get('other_sites', []):
            other_sites.append(OtherSite(
                site_type=site.get('site_type', 'USD'),
                amount=site.get('amount', 0)
            ))
        
        advances = []
        for advance in form_data.get('advances', []):
            advances.append(Advance(
                date=advance.get('date', ''),
                amount=advance.get('amount', 0)
            ))
        
        extras = []
        for extra in form_data.get('extras', []):
            extras.append(Advance(
                date=extra.get('date', ''),
                amount=extra.get('amount', 0)
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
            extras=extras,
            fines_count=form_data.get('fines_count', 0),
            custom_fine_cop=form_data.get('custom_fine_cop', 0),
            override_high_tokens_trm=bool(form_data.get('override_high_tokens_trm', False)),
            disable_bonus=bool(form_data.get('disable_bonus', False))
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
            'extras': [
                {'date': extra.date, 'amount': extra.amount}
                for extra in data.extras
            ],
            'fines_count': data.fines_count,
            'custom_fine_cop': data.custom_fine_cop,
            'override_high_tokens_trm': getattr(data, 'override_high_tokens_trm', False)
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
        
        extras = [
            Advance(extra['date'], extra['amount'])
            for extra in data_dict.get('extras', [])
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
            extras=extras,
            fines_count=data_dict.get('fines_count', 0),
            custom_fine_cop=data_dict.get('custom_fine_cop', 0),
            override_high_tokens_trm=bool(data_dict.get('override_high_tokens_trm', False)),
            disable_bonus=bool(data_dict.get('disable_bonus', False))
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
            'usd_to_send_platform': getattr(result, 'usd_to_send_platform', 0.0),
            'date': result.date,
            'total_tokens_all_sites': getattr(result, 'total_tokens_all_sites', 0.0),
            'bonus_percentage': getattr(result, 'bonus_percentage', 0.0),
            'bonus_amount_usd': getattr(result, 'bonus_amount_usd', 0.0),
            'bonus_amount_cop': getattr(result, 'bonus_amount_cop', 0.0),
            'original_percentage': getattr(result, 'original_percentage', 0.0),
            'final_percentage': getattr(result, 'final_percentage', 0.0)
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
            usd_to_send_platform=result_dict.get('usd_to_send_platform', 0),
            date=result_dict.get('date', ''),
            total_tokens_all_sites=result_dict.get('total_tokens_all_sites', 0.0),
            bonus_percentage=result_dict.get('bonus_percentage', 0.0),
            bonus_amount_usd=result_dict.get('bonus_amount_usd', 0.0),
            bonus_amount_cop=result_dict.get('bonus_amount_cop', 0.0),
            original_percentage=result_dict.get('original_percentage', 0.0),
            final_percentage=result_dict.get('final_percentage', 0.0)
        )


def main():
    """Main entry point."""
    try:
        app = ApplicationController()
        
        root = tk.Tk()
        app.initialize_gui(root)
        
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Application failed to start: {str(e)}"
        print(f"ERROR: {error_msg}")
        if 'root' in locals():
            messagebox.showerror("Application Error", error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
