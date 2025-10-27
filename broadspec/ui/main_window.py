"""
Main GUI window for BroadSpec Payment Calculator.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Dict, Any, Optional

from core.exceptions import BroadSpecError, CalculationError, VaultError
from utils.formatters import format_currency_cop, format_currency_usd


class BroadSpecGUI:
    """Main GUI application class implementing the View in MVC pattern."""
    
    def __init__(self, root: tk.Tk, config: Dict[str, Any], controller):
        """Initialize the GUI."""
        self.root = root
        self.config = config
        self.controller = controller
        
        # Store current calculation data
        self.current_input_data = None
        self.current_result_data = None
        
        # Set up window properties
        self.root.title("BroadSpec Payment Calculator")
        
        # Get UI dimensions from config or use defaults
        ui_config = config.get('ui', {})
        width = ui_config.get('default_width', 1900)
        height = ui_config.get('default_height', 1064)
        
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Make root gridable
        try:
            self.root.rowconfigure(0, weight=1)
            self.root.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        # Create main container with scrollbar
        main_canvas = tk.Canvas(root)
        main_scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Ensure the scrollable_frame expands inside canvas
        try:
            scrollable_frame.columnconfigure(0, weight=1)
            scrollable_frame.rowconfigure(0, weight=1)
        except Exception:
            pass
        
        # Create notebook with Main and Admin tabs
        self.notebook = ttk.Notebook(scrollable_frame)
        self.main_tab = ttk.Frame(self.notebook)
        self.admin_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main")
        self.notebook.add(self.admin_tab, text="Admin")
        self.notebook.pack(fill="both", expand=True)
        
        # Initialize UI components
        self._create_main_tab()
        self._create_admin_tab()
    
    def _create_main_tab(self):
        """Create the main calculator tab."""
        # Main tab frame
        main_frame = ttk.Frame(self.main_tab, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        try:
            self.main_tab.rowconfigure(0, weight=1)
            self.main_tab.columnconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.columnconfigure(1, weight=2)
            main_frame.columnconfigure(2, weight=1)
            main_frame.rowconfigure(1, weight=1)
        except Exception:
            pass
        
        # Title
        title = ttk.Label(main_frame, text="BROADSPEC PAYMENT CALCULATOR", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input fields column
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=(0, 20))
        
        try:
            input_frame.columnconfigure(0, weight=0)
            input_frame.columnconfigure(1, weight=1)
        except Exception:
            pass
        
        self._create_input_fields(input_frame)
        
        # Receipt displays
        self._create_receipt_displays(main_frame)
    
    def _create_input_fields(self, parent):
        """Create input field widgets."""
        row = 0
        
        # Model ID
        ttk.Label(parent, text="Model ID #:", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.model_id = ttk.Entry(parent, width=20)
        self.model_id.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Model name
        ttk.Label(parent, text="Model Name:", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.model_name = ttk.Entry(parent, width=20)
        self.model_name.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # TRM inputs
        ttk.Label(parent, text="TRM Official $COP (NOT NULL):", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.trm_official_cop = ttk.Entry(parent, width=20)
        self.trm_official_cop.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(parent, text="BTK TRM $COP:", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.btk_trm_cop = ttk.Entry(parent, width=20)
        self.btk_trm_cop.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Tokens
        ttk.Label(parent, text="Tokens (TKS):", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tokens = ttk.Entry(parent, width=20)
        self.tokens.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Percentage
        ttk.Label(parent, text="Percentage:", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.percentage = ttk.Combobox(parent, width=17, state='readonly')
        self.percentage['values'] = ('60%', '70%', '75%')
        self.percentage.current(1)
        self.percentage.bind('<<ComboboxSelected>>', self.on_percentage_change)
        self.percentage.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Other Sites section
        ttk.Label(parent, text="Other Sites (USD or TKS):", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5,5))
        row += 1
        
        other_sites_frame = ttk.Frame(parent)
        other_sites_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.other_sites_list_frame = ttk.Frame(other_sites_frame)
        self.other_sites_list_frame.pack(fill='x')
        
        add_other_site_btn = ttk.Button(other_sites_frame, text="+ Add Other Site", command=self.add_other_site_field)
        add_other_site_btn.pack(pady=5)
        row += 1
        
        # Previous Fortnight
        ttk.Label(parent, text="Previous Fortnight USD:", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.previous_fortnight_usd = ttk.Entry(parent, width=20)
        self.previous_fortnight_usd.insert(0, "0")
        self.previous_fortnight_usd.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Advances section
        ttk.Label(parent, text="Advances:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10,5))
        row += 1
        
        self.advances_entries = []
        
        advances_frame = ttk.Frame(parent)
        advances_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.advances_list_frame = ttk.Frame(advances_frame)
        self.advances_list_frame.pack(fill='x')
        
        add_advance_btn = ttk.Button(advances_frame, text="+ Add Advance", command=self.add_advance_field)
        add_advance_btn.pack(pady=5)
        row += 1
        
        # Fines section
        self.fines_label = ttk.Label(parent, text="Fines (Studio only):", font=('Arial', 10, 'bold'))
        self.fines_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10,5))
        row += 1
        
        self.fines_count_label = ttk.Label(parent, text="Number of Fines (30k each):", font=('Arial', 9))
        self.fines_count_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        self.fines_count = ttk.Entry(parent, width=20)
        self.fines_count.insert(0, "0")
        self.fines_count.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        self.custom_fine_label = ttk.Label(parent, text="OR Custom Fine Amount (COP):", font=('Arial', 9))
        self.custom_fine_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        self.custom_fine_cop = ttk.Entry(parent, width=20)
        self.custom_fine_cop.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        calc_btn = ttk.Button(buttons_frame, text="Calculate", command=self.calculate)
        calc_btn.grid(row=0, column=0, padx=5)
        
        clear_btn = ttk.Button(buttons_frame, text="Clear", command=self.clear_fields)
        clear_btn.grid(row=0, column=1, padx=5)
        
        save_btn = ttk.Button(buttons_frame, text="Save PDF", command=self.save_pdf)
        save_btn.grid(row=0, column=2, padx=5)
        
        # Add initial fields
        self.add_advance_field()
        self.add_other_site_field()
        self.on_percentage_change(None)
    
    def _create_receipt_displays(self, parent):
        """Create receipt display areas."""
        # Full receipt (middle)
        full_receipt_frame = ttk.LabelFrame(parent, text="Full Receipt (Internal)", padding="10")
        full_receipt_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        
        try:
            full_receipt_frame.rowconfigure(0, weight=1)
            full_receipt_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        self.full_receipt_text = tk.Text(full_receipt_frame, wrap='none')
        self.full_receipt_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar1 = ttk.Scrollbar(full_receipt_frame, orient=tk.VERTICAL, command=self.full_receipt_text.yview)
        scrollbar1.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.full_receipt_text['yscrollcommand'] = scrollbar1.set
        
        # Simplified receipt (right side)
        simple_receipt_frame = ttk.LabelFrame(parent, text="Model Receipt (Screenshot)", padding="10")
        simple_receipt_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        try:
            simple_receipt_frame.rowconfigure(0, weight=1)
            simple_receipt_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        self.simple_receipt_text = tk.Text(simple_receipt_frame, wrap='none')
        self.simple_receipt_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _create_admin_tab(self):
        """Create the admin tab for vault management."""
        if not self.controller.vault_repository:
            # Show message if vault is not available
            no_vault_label = ttk.Label(
                self.admin_tab, 
                text="Vault features are not available (cryptography package missing)",
                font=('Arial', 12)
            )
            no_vault_label.pack(pady=50)
            return
        
        # Create vault management UI
        vault_frame = ttk.LabelFrame(self.admin_tab, text="Encrypted Vault (Admin)", padding="10")
        vault_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=10)
        
        # Listbox for vault entries
        self.vault_listbox = tk.Listbox(vault_frame, width=100, height=20, selectmode=tk.EXTENDED)
        self.vault_listbox.grid(row=0, column=0, rowspan=4, sticky=(tk.W, tk.N))
        
        scrollbar = ttk.Scrollbar(vault_frame, orient=tk.VERTICAL, command=self.vault_listbox.yview)
        scrollbar.grid(row=0, column=1, rowspan=4, sticky=(tk.N, tk.S))
        self.vault_listbox['yscrollcommand'] = scrollbar.set
        
        # Buttons
        btn_frame = ttk.Frame(vault_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5,0))
        
        export_btn = ttk.Button(btn_frame, text="Export Selected", command=self.export_selected)
        export_btn.grid(row=0, column=0, padx=5)
        
        delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected)
        delete_btn.grid(row=0, column=1, padx=5)
        
        import_btn = ttk.Button(btn_frame, text="Import PDFs", command=self.import_pdfs)
        import_btn.grid(row=0, column=2, padx=5)
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_vault)
        refresh_btn.grid(row=0, column=3, padx=5)
        
        # Stats
        stats_frame = ttk.Frame(vault_frame)
        stats_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10,0))
        
        self.vault_count_label = ttk.Label(stats_frame, text="Entries: 0")
        self.vault_count_label.grid(row=0, column=0, sticky=tk.W, padx=(0,10))
        
        self.vault_size_label = ttk.Label(stats_frame, text="Vault size: 0 B")
        self.vault_size_label.grid(row=0, column=1, sticky=tk.W)
        
        # Initial load
        self.refresh_vault()
    
    # Event handlers
    
    def on_percentage_change(self, event):
        """Enable/disable fines based on percentage selection."""
        try:
            perc_str = self.percentage.get()
            percentage = float(perc_str.strip('%')) / 100
            
            if percentage > 0.60:
                # Disable fines for home workers
                self.fines_count.config(state='disabled')
                self.custom_fine_cop.config(state='disabled')
                self.fines_count.delete(0, tk.END)
                self.fines_count.insert(0, "0")
                self.custom_fine_cop.delete(0, tk.END)
                self.fines_label.config(text="Fines (Disabled - Home Worker)")
            else:
                # Enable fines for studio workers
                self.fines_count.config(state='normal')
                self.custom_fine_cop.config(state='normal')
                self.fines_label.config(text="Fines (Studio only):")
        except Exception:
            pass
    
    def add_advance_field(self):
        """Add a new advance entry field."""
        frame = ttk.Frame(self.advances_list_frame)
        frame.pack(pady=2)
        
        date_entry = ttk.Entry(frame, width=12)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(side=tk.LEFT, padx=2)
        
        amount_entry = ttk.Entry(frame, width=12)
        amount_entry.insert(0, "0")
        amount_entry.pack(side=tk.LEFT, padx=2)
        
        remove_btn = ttk.Button(frame, text="X", width=3, 
                               command=lambda: self.remove_advance_field(frame))
        remove_btn.pack(side=tk.LEFT, padx=2)
        
        self.advances_entries.append((date_entry, amount_entry, frame))
    
    def remove_advance_field(self, frame):
        """Remove an advance entry field."""
        for i, (date_e, amount_e, f) in enumerate(self.advances_entries):
            if f == frame:
                self.advances_entries.pop(i)
                frame.destroy()
                break
        
        # Keep at least one entry
        if len(self.advances_entries) == 0:
            self.add_advance_field()
    
    def add_other_site_field(self):
        """Add a new other-site entry field."""
        frame = ttk.Frame(self.other_sites_list_frame)
        frame.pack(pady=2)
        
        site_type_cb = ttk.Combobox(frame, width=6, state='readonly')
        site_type_cb['values'] = ('USD', 'TKS')
        site_type_cb.current(0)
        site_type_cb.pack(side=tk.LEFT, padx=2)
        
        amount_entry = ttk.Entry(frame, width=12)
        amount_entry.insert(0, "0")
        amount_entry.pack(side=tk.LEFT, padx=2)
        
        remove_btn = ttk.Button(frame, text="X", width=3,
                               command=lambda: self.remove_other_site_field(frame))
        remove_btn.pack(side=tk.LEFT, padx=2)
        
        if not hasattr(self, 'other_sites_entries'):
            self.other_sites_entries = []
        self.other_sites_entries.append((site_type_cb, amount_entry, frame))
    
    def remove_other_site_field(self, frame):
        """Remove an other-site entry field."""
        for i, (type_cb, amount_e, f) in enumerate(self.other_sites_entries):
            if f == frame:
                self.other_sites_entries.pop(i)
                frame.destroy()
                break
        
        # Keep at least one entry
        if len(self.other_sites_entries) == 0:
            self.add_other_site_field()
    
    def clear_fields(self):
        """Clear all input fields."""
        self.model_id.delete(0, tk.END)
        self.model_name.delete(0, tk.END)
        self.tokens.delete(0, tk.END)
        self.percentage.current(1)
        self.previous_fortnight_usd.delete(0, tk.END)
        self.previous_fortnight_usd.insert(0, "0")
        
        # Clear other sites
        if hasattr(self, 'other_sites_entries'):
            for type_cb, amount_e, frame in self.other_sites_entries:
                frame.destroy()
            self.other_sites_entries = []
            self.add_other_site_field()
        
        # Clear advances
        for date_e, amount_e, frame in self.advances_entries:
            frame.destroy()
        self.advances_entries = []
        self.add_advance_field()
        
        # Clear fines
        self.fines_count.delete(0, tk.END)
        self.fines_count.insert(0, "0")
        self.custom_fine_cop.delete(0, tk.END)
        
        # Clear receipts
        self.full_receipt_text.delete(1.0, tk.END)
        self.simple_receipt_text.delete(1.0, tk.END)
        
        # Reset stored data
        self.current_input_data = None
        self.current_result_data = None
        
        # Reset fines state
        self.on_percentage_change(None)
    
    def calculate(self):
        """Perform payment calculation."""
        try:
            # Get form data
            form_data = self._get_form_data()
            
            # Calculate using controller
            input_data, result_data = self.controller.calculate_payment(form_data)
            
            # Store results
            self.current_input_data = input_data
            self.current_result_data = result_data
            
            # Display receipts
            self._display_receipts(input_data, result_data)
            
        except BroadSpecError as e:
            messagebox.showerror("Calculation Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")
    
    def save_pdf(self):
        """Save receipt as PDF."""
        if not self.current_input_data or not self.current_result_data:
            messagebox.showwarning("No Data", "Please calculate first before saving")
            return
        
        try:
            pdf_path = self.controller.save_receipt(self.current_input_data, self.current_result_data)
            messagebox.showinfo("Success", f"PDF saved to:\n{pdf_path}")
        except BroadSpecError as e:
            messagebox.showerror("Save Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")
    
    def export_selected(self):
        """Export selected vault entries."""
        if not self.controller.vault_repository:
            return
        
        selection = self.vault_listbox.curselection()
        if not selection:
            messagebox.showinfo("Export", "Please select entries to export")
            return
        
        try:
            if len(selection) == 1:
                # Single file - ask for location
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
                )
                if not filepath:
                    return
            else:
                # Multiple files - ask for directory
                directory = filedialog.askdirectory(title="Select export directory")
                if not directory:
                    return
            
            exported = 0
            for idx in selection:
                if idx < len(self.vault_entries):
                    entry = self.vault_entries[idx]
                    vault_filename = entry.get('vault_filename')
                    
                    if len(selection) == 1:
                        export_path = filepath
                    else:
                        export_path = None
                    
                    try:
                        path = self.controller.export_from_vault(vault_filename, export_path)
                        exported += 1
                    except Exception as e:
                        print(f"Failed to export {vault_filename}: {str(e)}")
            
            messagebox.showinfo("Export", f"Exported {exported} file(s)")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def delete_selected(self):
        """Delete selected vault entries."""
        if not self.controller.vault_repository:
            return
        
        selection = self.vault_listbox.curselection()
        if not selection:
            messagebox.showinfo("Delete", "Please select entries to delete")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", f"Delete {len(selection)} selected entries?")
        if not confirm:
            return
        
        try:
            vault_filenames = []
            for idx in selection:
                if idx < len(self.vault_entries):
                    entry = self.vault_entries[idx]
                    vault_filenames.append(entry.get('vault_filename'))
            
            deleted_count = self.controller.delete_from_vault(vault_filenames)
            messagebox.showinfo("Delete", f"Deleted {deleted_count} file(s)")
            self.refresh_vault()
            
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete: {str(e)}")
    
    def import_pdfs(self):
        """Import PDF files to vault."""
        if not self.controller.vault_repository:
            return
        
        filepaths = filedialog.askopenfilenames(
            title="Select PDF files to import",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not filepaths:
            return
        
        try:
            success_count, failure_count = self.controller.import_to_vault(list(filepaths))
            
            if failure_count > 0:
                messagebox.showwarning("Import", 
                    f"Imported {success_count} file(s)\nFailed to import {failure_count} file(s)")
            else:
                messagebox.showinfo("Import", f"Successfully imported {success_count} file(s)")
            
            self.refresh_vault()
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {str(e)}")
    
    def refresh_vault(self):
        """Refresh vault entries list."""
        if not self.controller.vault_repository:
            return
        
        try:
            self.vault_entries = self.controller.get_vault_entries()
            self.vault_listbox.delete(0, tk.END)
            
            if not self.vault_entries:
                self.vault_listbox.insert(tk.END, "No entries in vault")
            else:
                for i, entry in enumerate(self.vault_entries, start=1):
                    filename = entry.get('orig_filename', 'Unknown')
                    display = f"{i}. {filename}"
                    self.vault_listbox.insert(tk.END, display)
            
            # Update stats
            stats = self.controller.get_vault_stats()
            self.vault_count_label.config(text=f"Entries: {stats['count']}")
            self.vault_size_label.config(text=f"Vault size: {self._format_size(stats['size'])}")
            
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh vault: {str(e)}")
    
    # Helper methods
    
    def _get_form_data(self) -> dict:
        """Collect data from form fields."""
        # Get other sites
        other_sites = []
        for type_cb, amount_e, _ in getattr(self, 'other_sites_entries', []):
            try:
                amount = float(amount_e.get() or 0)
                if amount > 0:
                    other_sites.append({
                        'site_type': type_cb.get(),
                        'amount': amount
                    })
            except ValueError:
                pass
        
        # Get advances
        advances = []
        for date_e, amount_e, _ in self.advances_entries:
            try:
                amount = float(amount_e.get() or 0)
                advances.append({
                    'date': date_e.get(),
                    'amount': amount
                })
            except ValueError:
                pass
        
        # Get fines
        custom_fine = (self.custom_fine_cop.get() or "").strip().replace(",", "")
        if custom_fine:
            fines_count = 0
            custom_fine_cop = float(custom_fine)
        else:
            fines_count = int(self.fines_count.get() or 0)
            custom_fine_cop = 0
        
        # Get percentage
        perc_str = self.percentage.get()
        percentage = float(perc_str.strip('%')) / 100
        
        return {
            'model_id': self.model_id.get().strip(),
            'model_name': self.model_name.get(),
            'trm_official_cop': float(self.trm_official_cop.get()),
            'btk_trm_cop': float(self.btk_trm_cop.get()),
            'tokens': int(self.tokens.get()),
            'percentage': percentage,
            'previous_fortnight_usd': float(self.previous_fortnight_usd.get() or 0),
            'other_sites': other_sites,
            'advances': advances,
            'fines_count': fines_count,
            'custom_fine_cop': custom_fine_cop
        }
    
    def _display_receipts(self, input_data: dict, result_data: dict):
        """Display calculation results in receipt text areas."""
        # Generate full receipt
        full_receipt = self._generate_full_receipt(input_data, result_data)
        self.full_receipt_text.delete(1.0, tk.END)
        self.full_receipt_text.insert(1.0, full_receipt)
        
        # Generate simple receipt
        simple_receipt = self._generate_simple_receipt(input_data, result_data)
        self.simple_receipt_text.delete(1.0, tk.END)
        self.simple_receipt_text.insert(1.0, simple_receipt)
    
    def _generate_full_receipt(self, input_data: dict, result_data: dict) -> str:
        """Generate full receipt text."""
        equals_line = "=" * 50
        
        # Format other sites
        other_sites_lines = []
        for i, site in enumerate(input_data.get('other_sites', []), start=2):
            if site['site_type'] == 'USD':
                other_sites_lines.append(f"    Site {i}: {format_currency_usd(site['amount'])} USD")
            else:
                usd_amt = site['amount'] / 20.0
                other_sites_lines.append(f"    Site {i}: {int(site['amount']):,} TKS => {format_currency_usd(usd_amt)} USD")
        
        other_sites_display = "\n".join(other_sites_lines) if other_sites_lines else "    None"
        
        # Format advances
        advances_lines = []
        for advance in input_data.get('advances', []):
            advances_lines.append(f"    {advance['date']}: {format_currency_cop(advance['amount'])}")
        
        advances_display = "\n".join(advances_lines) if advances_lines else "    None"
        if advances_display:
            advances_display += "\n"
        
        # Format fines
        fines_display = result_data.get('fines_display', '')
        if not result_data.get('show_fines', True):
            fines_display = "Fines: Disabled (Home Worker)"
        
        return f"""
{equals_line}
            PAYMENT RECEIPT
              BROADSPEC
{equals_line}
Model ID: {input_data.get('model_id', '')}
Model: {input_data.get('model_name', '')}
Date: {result_data.get('date', '')}
{equals_line}
  
INPUT VALUES:
  TRM Official $COP: {format_currency_cop(input_data.get('trm_official_cop', 0))}
  TRM BROADSPEC $COP: {format_currency_cop(result_data.get('trm_broadspec_cop', 0))}
  Tokens (TKS): {input_data.get('tokens', 0):,}
  Percentage: {input_data.get('percentage', 0):.0%}
  Other Sites (USD equivalent):
{other_sites_display}
  Previous Fortnight USD: {format_currency_usd(input_data.get('previous_fortnight_usd', 0))}
  
ADVANCES:
{advances_display}  Total: {format_currency_cop(result_data.get('advances_total', 0))}
  
FINES:
  {fines_display}
  
CALCULATED VALUES:
  USD from Tokens: {format_currency_usd(result_data.get('usd_from_tokens', 0))}
  Net Amount USD: {format_currency_usd(result_data.get('net_usd', 0))}
  Total USD (Pre-calc): {format_currency_usd(result_data.get('total_usd_precalc', 0))}
  Total USD in COP: {format_currency_cop(result_data.get('total_usd_precalc', 0) * result_data.get('trm_broadspec_cop', 1))}
  Transfer Cost: {format_currency_cop(result_data.get('transfer_cost_cop', 0))}
  
FINAL CALCULATION:
  BroadSpec Value: {format_currency_cop(result_data.get('valor_broadspec_cop', 0))}
  Less Advances: {format_currency_cop(result_data.get('advances_total', 0))}
  Less Fines: {format_currency_cop(result_data.get('fines_total', 0))}
   
  TOTAL PAYMENT: {format_currency_cop(result_data.get('total_cop', 0))}
  TOTAL PAYMENT: {format_currency_usd(result_data.get('total_usd', 0))}
 
{equals_line}
     Payment calculation completed
{equals_line}
"""
    
    def _generate_simple_receipt(self, input_data: dict, result_data: dict) -> str:
        """Generate simple receipt text."""
        equals_line = "=" * 40
        
        # Format other sites
        other_sites_lines = []
        for i, site in enumerate(input_data.get('other_sites', []), start=2):
            if site['site_type'] == 'USD':
                other_sites_lines.append(f"  Site {i}: {format_currency_usd(site['amount'])}")
            else:
                other_sites_lines.append(f"  Site {i}: {int(site['amount']):,} TKS")
        
        other_sites_display = "\n".join(other_sites_lines) if other_sites_lines else "  None"
        
        # Format advances
        advances_lines = []
        for advance in input_data.get('advances', []):
            # Only include advances with non-zero amounts
            if advance['amount'] > 0:
                advances_lines.append(f"  {advance['date']}: {format_currency_cop(advance['amount'], show_decimals=False)}")
        
        advances_display = "\n".join(advances_lines) if advances_lines else "  None"
        # Always add newline after advances section
        advances_display += "\n"
        
        # Format fines section
        fines_section = ""
        if result_data.get('show_fines', True):
            fines_section = f"Fines: {format_currency_cop(result_data.get('fines_total', 0))}\n\n"
        
        return f"""
        
        
        BROADSPEC
      Payment Summary
   
   
{equals_line}
  
Date: {result_data.get('date', '')}
  
ID: {input_data.get('model_id', '')}
  
Model: {input_data.get('model_name', '')}
  
TRM Official: {format_currency_cop(input_data.get('trm_official_cop', 0))}
 
TRM BroadSpec: {format_currency_cop(result_data.get('trm_broadspec_cop', 0))}
  
Tokens: {input_data.get('tokens', 0):,}
  
Other Sites:
{other_sites_display}
  
Percentage: {input_data.get('percentage', 0):.0%}
  
Advances:
{advances_display}{fines_section}Total Payment:
{format_currency_cop(result_data.get('total_cop', 0))}
  
{equals_line}
  
  
"""
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        try:
            for unit in ['B','KB','MB','GB','TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:3.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} PB"
        except Exception:
            return f"{size_bytes} B"