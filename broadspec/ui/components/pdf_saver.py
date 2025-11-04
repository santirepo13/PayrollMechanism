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
        """Save receipt as a PDF file."""
        if not self.window_setup.current_input_data or not self.window_setup.current_result_data:
            messagebox.showwarning("No Data", "Please calculate first before saving")
            return

        try:
            receipts_dir = os.path.join(os.getcwd(), "Receipts")
            os.makedirs(receipts_dir, exist_ok=True)

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

            try:
                pdf_name = generate_filename(self.window_setup.current_input_data, result_obj)
            except Exception:
                model_id = (self.window_setup.current_input_data.get('model_id') or "").strip()
                model_name = (self.window_setup.current_input_data.get('model_name') or "").strip()
                date_str = (self.window_setup.current_result_data.get('date') or datetime.now().strftime("%Y-%m-%d"))
                pdf_name = f"{model_id} - {model_name} - {date_str}.pdf"

            pdf_path = os.path.join(receipts_dir, pdf_name)

            pdf_path_to_import = None
            if hasattr(self.controller, 'save_receipt'):
                saved_path = self.controller.save_receipt(self.window_setup.current_input_data, self.window_setup.current_result_data)
                if not saved_path:
                    raise Exception("Controller.save_receipt did not return a path")
                pdf_path_to_import = os.path.abspath(saved_path)
            elif hasattr(self.controller, 'generate_receipt_pdf'):
                self.controller.generate_receipt_pdf(self.window_setup.current_input_data, self.window_setup.current_result_data, pdf_path)
                pdf_path_to_import = os.path.abspath(pdf_path)
            else:
                raise Exception('Controller does not support PDF generation API')

            if not hasattr(self.controller, 'import_to_vault'):
                raise Exception('Vault import API is not available on controller')

            if hasattr(self.controller, 'save_receipt'):
                try:
                    messagebox.showinfo('Saved', f'PDF saved by controller: {pdf_path_to_import}')
                    try:
                        if hasattr(self.main_tab_ui, 'refresh_vault'):
                            self.main_tab_ui.refresh_vault()
                    except Exception:
                        pass
                except Exception:
                    pass
            else:
                try:
                    success_count, failure_count = self.controller.import_to_vault([pdf_path_to_import])

                    if success_count > 0:
                        messagebox.showinfo('Saved to Vault', f'PDF saved to encrypted vault. Use Admin tab to export. Imported: {success_count}, Failed: {failure_count}')
                        try:
                            if hasattr(self.main_tab_ui, 'refresh_vault'):
                                self.main_tab_ui.refresh_vault()
                        except Exception:
                            pass
                    else:
                        messagebox.showwarning('Vault Import', f'No files were imported to vault. Failures: {failure_count}')
                except Exception as e:
                    messagebox.showerror("Vault Import Error", f"Failed to import to vault: {str(e)}")

        except BroadSpecError as e:
            messagebox.showerror("Save Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")