import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from broadspec.core.exceptions import BroadSpecError
from broadspec.utils.pdf_protocols import generate_filename


class PDFSaver:
    """Handles saving receipts as PDF files."""
    
    def __init__(self, main_tab_ui, window_setup, controller):
        """Initialize PDF saver."""
        self.main_tab_ui = main_tab_ui
        self.window_setup = window_setup
        self.controller = controller
        
        self.main_tab_ui.save_pdf_btn.config(command=self.save_pdf)
    
    def save_pdf(self):
        """Save receipt directly into the encrypted vault (no local file)."""
        if not self.window_setup.current_input_data or not self.window_setup.current_result_data:
            messagebox.showwarning("No Data", "Please calculate first before saving")
            return

        try:
            # Build a small result object for filename generation if possible
            result_obj = None
            try:
                if hasattr(self.controller, '_dict_to_calculation_result'):
                    result_obj = self.controller._dict_to_calculation_result(self.window_setup.current_result_data)
                else:
                    class _R:
                        pass
                    result_obj = _R()
                    result_obj.date = self.window_setup.current_result_data.get('date', datetime.now().strftime("%Y-%m-%d"))
                    result_obj.total_usd = self.window_setup.current_result_data.get('total_usd', 0)
                    result_obj.total_cop = self.window_setup.current_result_data.get('total_cop', 0)
            except Exception:
                result_obj = None

            # Build filename (used only as the vault's internal filename)
            try:
                pdf_name = generate_filename(self.window_setup.current_input_data, result_obj)
            except Exception:
                model_id = (self.window_setup.current_input_data.get('model_id') or "").strip()
                model_name = (self.window_setup.current_input_data.get('model_name') or "").strip()
                date_str = (self.window_setup.current_result_data.get('date') or datetime.now().strftime("%Y-%m-%d"))
                pdf_name = f"{model_id} - {model_name} - {date_str}.pdf"

            # Controller must implement save_receipt which saves directly into vault
            if hasattr(self.controller, 'save_receipt'):
                try:
                    vault_filename = self.controller.save_receipt(self.window_setup.current_input_data, self.window_setup.current_result_data)
                    if not vault_filename:
                        raise Exception("Controller.save_receipt did not return a vault filename")
                    messagebox.showinfo('Saved to Vault', f'PDF saved to encrypted vault as: {vault_filename}')
                    try:
                        if hasattr(self.main_tab_ui, 'refresh_vault'):
                            self.main_tab_ui.refresh_vault()
                    except Exception:
                        pass
                except Exception as e:
                    messagebox.showerror("Vault Save Error", f"Failed to save PDF to vault: {str(e)}")
            else:
                # If controller doesn't support saving directly to vault, show clear error
                messagebox.showerror("Save Error", "Controller does not support saving receipts directly to the vault. Enable vault support.")
                return

        except BroadSpecError as e:
            messagebox.showerror("Save Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")