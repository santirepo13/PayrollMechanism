"""
Main GUI window for BroadSpec Payment Calculator.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Dict, Any, Optional
from PIL import Image, ImageTk

from broadspec.core.exceptions import BroadSpecError, CalculationError, VaultError
from broadspec.utils.formatters import format_currency_cop, format_currency_usd
from broadspec.utils.pdf_preview import PDFPreviewer


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
        
        # Initialize PDF previewer
        self.pdf_previewer = PDFPreviewer(config)
        
        # Set up window properties
        self.root.title("BroadSpec Payment Calculator")
        
        # Get UI dimensions from config or use defaults
        ui_config = config.get('ui', {})
        width = ui_config.get('default_width', 1900)
        height = ui_config.get('default_height', 1064)
        
        # Adjust height to account for taskbar (approximately 40 pixels)
        self.taskbar_height = 40
        adjusted_height = height - self.taskbar_height
        
        self.root.geometry(f"{width}x{adjusted_height}")
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
        
        # Create main container (single box layout)
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame to expand
        try:
            self.main_frame.rowconfigure(0, weight=1)
            self.main_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        # Create notebook with Main and Admin tabs
        self.notebook = ttk.Notebook(self.main_frame)
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
        main_frame = ttk.Frame(self.main_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        try:
            self.main_tab.rowconfigure(0, weight=1)
            self.main_tab.columnconfigure(0, weight=1)
            # Keep the input column compact and allow receipt area to expand
            main_frame.columnconfigure(0, weight=0, minsize=320)
            main_frame.columnconfigure(1, weight=3)
            main_frame.columnconfigure(2, weight=0)
            main_frame.rowconfigure(1, weight=1)
            main_frame.rowconfigure(2, weight=0)  # For action buttons
        except Exception:
            pass
        
        # Title
        title = ttk.Label(main_frame, text="BROADSPEC PAYMENT CALCULATOR",
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Input fields column
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=(0, 10))
        
        try:
            input_frame.columnconfigure(0, weight=0)
            input_frame.columnconfigure(1, weight=1)
        except Exception:
            pass
        
        self._create_input_fields(input_frame)
        
        # Receipt displays
        self._create_receipt_displays(main_frame)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(action_frame, text="Calculate", command=self.calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Clear Fields", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Save PDF", command=self.save_pdf).pack(side=tk.LEFT, padx=5)
        
    
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
        
        # No buttons here - they're now in the main tab
        
        
        # Add initial fields
        self.add_advance_field()
        self.add_other_site_field()
        self.on_percentage_change(None)
    
    def _create_receipt_displays(self, parent):
        """Create receipt display area with dual box layout (full receipt and model screenshot)."""
        # Create a container for the receipt displays
        receipt_container = ttk.Frame(parent)
        receipt_container.grid(row=1, column=1, columnspan=2, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        try:
            receipt_container.columnconfigure(0, weight=1)
            receipt_container.columnconfigure(1, weight=1)
            receipt_container.rowconfigure(0, weight=1)
        except Exception:
            pass
        
        # Full receipt display
        full_receipt_frame = ttk.LabelFrame(receipt_container, text="Full Receipt", padding="10")
        full_receipt_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        try:
            full_receipt_frame.rowconfigure(0, weight=1)
            full_receipt_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        self.receipt_text = tk.Text(full_receipt_frame, wrap='none', font=('Courier', 10), width=80)
        self.receipt_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(full_receipt_frame, orient=tk.VERTICAL, command=self.receipt_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.receipt_text['yscrollcommand'] = scrollbar.set
        
        # Model screenshot display (for payment confirmation)
        model_frame = ttk.LabelFrame(receipt_container, text="Payment Confirmation", padding="10")
        model_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        try:
            model_frame.rowconfigure(0, weight=1)
            model_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        self.model_text = tk.Text(model_frame, wrap='none', height=15, font=('Courier', 10), width=50)
        self.model_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        model_scrollbar = ttk.Scrollbar(model_frame, orient=tk.VERTICAL, command=self.model_text.yview)
        model_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.model_text['yscrollcommand'] = model_scrollbar.set
    
    def _create_admin_tab(self):
        """Create the admin tab for vault management."""
        # Create main container for admin tab
        admin_container = ttk.Frame(self.admin_tab, padding="10")
        admin_container.pack(fill=tk.BOTH, expand=True)
        
        if not self.controller.vault_repository:
            # Show message if vault is not available
            no_vault_label = ttk.Label(
                admin_container,
                text="Vault features are not available (cryptography package missing)",
                font=('Arial', 12)
            )
            no_vault_label.pack(pady=50)
            return
        
        # Create vault management UI
        vault_frame = ttk.LabelFrame(admin_container, text="Encrypted Vault (Admin)", padding="10")
        vault_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Listbox for vault entries
        self.vault_listbox = tk.Listbox(vault_frame, width=100, height=20, selectmode=tk.EXTENDED)
        self.vault_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vault_listbox.bind('<Double-Button-1>', self.on_vault_double_click)
        
        scrollbar = ttk.Scrollbar(vault_frame, orient=tk.VERTICAL, command=self.vault_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vault_listbox['yscrollcommand'] = scrollbar.set
        
        # Buttons
        btn_frame = ttk.Frame(admin_container)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        export_btn = ttk.Button(btn_frame, text="Export Selected", command=self.export_selected)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        import_btn = ttk.Button(btn_frame, text="Import PDFs", command=self.import_pdfs)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_vault)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Resolution toggle button
        self.resolution_var = tk.StringVar(value="1920x1080")
        resolution_btn = ttk.Button(btn_frame, text="Toggle Resolution", command=self.toggle_resolution)
        resolution_btn.pack(side=tk.LEFT, padx=5)
        
        # Current resolution label
        self.resolution_label = ttk.Label(btn_frame, textvariable=self.resolution_var)
        self.resolution_label.pack(side=tk.LEFT, padx=5)
        
        # Stats
        stats_frame = ttk.Frame(admin_container)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.vault_count_label = ttk.Label(stats_frame, text="Entries: 0")
        self.vault_count_label.pack(side=tk.LEFT, padx=(0,10))
        
        self.vault_size_label = ttk.Label(stats_frame, text="Vault size: 0 B")
        self.vault_size_label.pack(side=tk.LEFT)
        
        # Initial load
        self.refresh_vault()
        
        # Add PDF preview section to admin tab
        self._create_pdf_preview_in_admin()
    
    def _create_pdf_preview_tab(self):
        """Create the PDF preview tab."""
        if not self.pdf_previewer.is_enabled():
            # Show message if PDF preview is disabled
            no_preview_label = ttk.Label(
                self.pdf_preview_tab,
                text="PDF Preview is disabled in configuration",
                font=('Arial', 12)
            )
            no_preview_label.pack(pady=50)
            return
        
        # Create PDF preview UI
        preview_frame = ttk.Frame(self.pdf_preview_tab, padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        try:
            self.pdf_preview_tab.rowconfigure(0, weight=1)
            self.pdf_preview_tab.columnconfigure(0, weight=1)
            preview_frame.rowconfigure(1, weight=1)
            preview_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        # Controls frame
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
                # Navigation controls
        nav_frame = ttk.Frame(preview_frame)
        nav_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(nav_frame, text="Previous", command=self.prev_page).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="Next", command=self.next_page).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(nav_frame, text="Page:").pack(side=tk.LEFT, padx=(10, 2))
        self.page_var = tk.StringVar(value="0 / 0")
        ttk.Label(nav_frame, textvariable=self.page_var).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(nav_frame, text="Zoom:").pack(side=tk.LEFT, padx=(10, 2))
        self.zoom_var = tk.StringVar(value="100%")
        zoom_combo = ttk.Combobox(nav_frame, textvariable=self.zoom_var, width=8, state='readonly')
        zoom_combo['values'] = ('50%', '75%', '100%', '125%', '150%', '200%')
        zoom_combo.current(2)
        zoom_combo.bind('<<ComboboxSelected>>', self.on_zoom_change)
        zoom_combo.pack(side=tk.LEFT)
        
        # Create scrollable canvas for PDF display
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        
        try:
            canvas_frame.rowconfigure(0, weight=1)
            canvas_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        self.pdf_canvas = tk.Canvas(canvas_frame, bg="white")
        self.pdf_v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.pdf_canvas.yview)
        self.pdf_h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.pdf_canvas.xview)
        
        self.pdf_canvas.configure(yscrollcommand=self.pdf_v_scrollbar.set, xscrollcommand=self.pdf_h_scrollbar.set)
        
        self.pdf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.pdf_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pdf_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Store reference to current image to prevent garbage collection
        self.current_pdf_image = None
    
    def _create_pdf_preview_in_admin(self):
        """Create PDF preview section in admin tab."""
        if not self.pdf_previewer.is_enabled():
            # Show message if PDF preview is disabled
            no_preview_label = ttk.Label(
                self.admin_tab,
                text="PDF Preview is disabled in configuration",
                font=('Arial', 10)
            )
            no_preview_label.pack(pady=10)
            return
        
        # Create PDF preview frame in admin tab
        pdf_preview_frame = ttk.LabelFrame(self.admin_tab, text="PDF Preview", padding="10")
        pdf_preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for pdf_preview_frame
        try:
            pdf_preview_frame.rowconfigure(1, weight=1)
            pdf_preview_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
                # Create scrollable canvas for PDF display
        canvas_frame = ttk.Frame(pdf_preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        
        try:
            canvas_frame.rowconfigure(0, weight=1)
            canvas_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        self.admin_pdf_canvas = tk.Canvas(canvas_frame, bg="white", width=600, height=400)
        admin_pdf_v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.admin_pdf_canvas.yview)
        admin_pdf_h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.admin_pdf_canvas.xview)
        
        self.admin_pdf_canvas.configure(yscrollcommand=admin_pdf_v_scrollbar.set, xscrollcommand=admin_pdf_h_scrollbar.set)
        
        self.admin_pdf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        admin_pdf_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        admin_pdf_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Navigation controls
        nav_frame = ttk.Frame(pdf_preview_frame)
        nav_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(nav_frame, text="Previous", command=self.admin_prev_page).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="Next", command=self.admin_next_page).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(nav_frame, text="Page:").pack(side=tk.LEFT, padx=(10, 2))
        self.admin_page_var = tk.StringVar(value="0 / 0")
        ttk.Label(nav_frame, textvariable=self.admin_page_var).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(nav_frame, text="Zoom:").pack(side=tk.LEFT, padx=(10, 2))
        self.admin_zoom_var = tk.StringVar(value="100%")
        admin_zoom_combo = ttk.Combobox(nav_frame, textvariable=self.admin_zoom_var, width=8, state='readonly')
        admin_zoom_combo['values'] = ('50%', '75%', '100%', '125%', '150%', '200%')
        admin_zoom_combo.current(2)
        admin_zoom_combo.bind('<<ComboboxSelected>>', self.admin_on_zoom_change)
        admin_zoom_combo.pack(side=tk.LEFT)
        
        # Store reference to current image to prevent garbage collection
        self.admin_current_pdf_image = None
    
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
        self.receipt_text.delete(1.0, tk.END)
        self.model_text.delete(1.0, tk.END)
        
        # Reset stored data
        self.current_input_data = None
        self.current_result_data = None
        
        # Reset fines state
        self.on_percentage_change(None)
    
    def calculate(self):
        """Perform payment calculation."""
        try:
                form_data = self._get_form_data()
                input_data, result_data = self.controller.calculate_payment(form_data)
                self.current_input_data = input_data
                self.current_result_data = result_data
                self._display_receipts(input_data, result_data)
        except BroadSpecError as e:
                messagebox.showerror("Calculation Error", str(e))
        except Exception as e:
                messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")

    def save_pdf(self):
        if not self.current_input_data or not self.current_result_data:
            messagebox.showwarning("No Data", "Please calculate first before saving")
            return

        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name

            if hasattr(self.controller, 'generate_receipt_pdf'):
                self.controller.generate_receipt_pdf(self.current_input_data, self.current_result_data, temp_path)
            else:
                if hasattr(self.controller, 'save_receipt'):
                    saved_path = self.controller.save_receipt(self.current_input_data, self.current_result_data)
                    try:
                        with open(saved_path, 'rb') as src, open(temp_path, 'wb') as dst:
                            dst.write(src.read())
                    except Exception:
                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass
                        raise
                else:
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
                    raise Exception('Controller does not support PDF generation API')

            if not hasattr(self.controller, 'import_to_vault'):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
                raise Exception('Vault import API is not available on controller')

            success_count, failure_count = self.controller.import_to_vault([temp_path])

            try:
                os.remove(temp_path)
            except Exception:
                pass

            if success_count > 0:
                messagebox.showinfo('Saved to Vault', f'PDF saved to encrypted vault. Use Admin tab to export. Imported: {success_count}, Failed: {failure_count}')
                try:
                    self.refresh_vault()
                except Exception:
                    pass
            else:
                messagebox.showwarning('Vault Import', f'No files were imported to the vault. Failures: {failure_count}')

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
    
    def toggle_resolution(self):
        """Toggle between 1920x1080 and 1366x768 resolutions."""
        current_resolution = self.resolution_var.get()
        
        if current_resolution == "1920x1080":
            self.resolution_var.set("1366x768")
            new_width, new_height = 1366, 768
        else:
            self.resolution_var.set("1920x1080")
            new_width, new_height = 1920, 1080
        
        # Adjust height to account for taskbar
        adjusted_height = new_height - self.taskbar_height
        
        # Update the UI to fit the new resolution
        self._update_ui_for_resolution(new_width, adjusted_height)
    
    def _update_ui_for_resolution(self, width, height):
        """Update UI elements to fit the specified resolution."""
        # Calculate scaling factor based on 1920x1080 as reference
        scale_factor_width = width / 1920
        scale_factor_height = height / (1080 - self.taskbar_height)  # Adjust for taskbar
        
        # Use the smaller scale factor to maintain aspect ratio
        scale_factor = min(scale_factor_width, scale_factor_height)
        
        # Store current scale factor for later use
        self.current_scale_factor = scale_factor
        
        # Apply scaling to UI elements
        self._scale_ui_elements(scale_factor)
        
        # Adjust padding and spacing based on scale factor
        self._adjust_layout_spacing(scale_factor)
        
        # Adjust window size to ensure it fits within screen bounds
        self._adjust_window_size(width, height)
        
        # Scale receipt text content to fit resolution
        self._scale_receipt_content(scale_factor)
    
    def _scale_ui_elements(self, scale_factor):
        """Scale UI elements based on the scale factor."""
        # Update font sizes
        base_font_size = 10
        new_font_size = max(8, int(base_font_size * scale_factor))
        
        # Update title font
        title_font = ('Arial', max(14, int(16 * scale_factor)), 'bold')
        
        # Update input field fonts
        input_font = ('Arial', new_font_size)
        
        # Apply font changes to relevant elements
        try:
            # Update main tab elements
            for widget in self.main_tab.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Label):
                            child.config(font=input_font)
                        elif isinstance(child, ttk.Button):
                            child.config(font=input_font)
                        elif isinstance(child, ttk.Entry):
                            child.config(font=input_font)
                        elif isinstance(child, ttk.Combobox):
                            child.config(font=input_font)
                        elif isinstance(child, ttk.LabelFrame):
                            # Update frame labels
                            child.config(font=input_font)
                            # Update frame contents
                            for frame_child in child.winfo_children():
                                if isinstance(frame_child, ttk.Label):
                                    frame_child.config(font=input_font)
                                elif isinstance(frame_child, tk.Text):
                                    frame_child.config(font=('Courier New', new_font_size))
            
            # Update admin tab elements
            for widget in self.admin_tab.winfo_children():
                if isinstance(widget, ttk.Label):
                    widget.config(font=input_font)
                elif isinstance(widget, ttk.Button):
                    widget.config(font=input_font)
                elif isinstance(widget, ttk.Listbox):
                    widget.config(font=input_font)
                elif isinstance(widget, ttk.LabelFrame):
                    # Update frame labels
                    widget.config(font=input_font)
                    # Update frame contents
                    for frame_child in widget.winfo_children():
                        if isinstance(frame_child, ttk.Label):
                            frame_child.config(font=input_font)
                        elif isinstance(frame_child, ttk.Button):
                            frame_child.config(font=input_font)
                        elif isinstance(frame_child, tk.Listbox):
                            frame_child.config(font=input_font)
                        elif isinstance(frame_child, ttk.Entry):
                            frame_child.config(font=input_font)
                        elif isinstance(frame_child, ttk.Canvas):
                            # Adjust canvas size
                            canvas_width = int(600 * scale_factor)
                            canvas_height = int(400 * scale_factor)
                            frame_child.config(width=canvas_width, height=canvas_height)
            
            # Update notebook tab fonts
            style = ttk.Style()
            style.configure('TNotebook.Tab', font=input_font)
            
        except Exception as e:
            print(f"Error scaling UI elements: {str(e)}")
    
    def _adjust_layout_spacing(self, scale_factor):
        """Adjust padding and spacing based on scale factor."""
        try:
            # Scale padding values
            base_padding = 10
            scaled_padding = max(5, int(base_padding * scale_factor))
            
            # Update main frame padding
            self.main_frame.config(padding=scaled_padding)
            
            # Update notebook padding
            self.notebook.config(padding=scaled_padding)
            
            # Update tab frame paddings
            for tab in [self.main_tab, self.admin_tab]:
                for widget in tab.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        widget.config(padding=scaled_padding)
                    elif isinstance(widget, ttk.LabelFrame):
                        widget.config(padding=scaled_padding)
            
            # Scale button padding
            for tab in [self.main_tab, self.admin_tab]:
                for widget in tab.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Frame):  # Button frames
                                for btn in child.winfo_children():
                                    if isinstance(btn, ttk.Button):
                                        # Scale button padding
                                        padx = max(2, int(5 * scale_factor))
                                        pady = max(2, int(5 * scale_factor))
                                        btn.grid_configure(padx=padx, pady=pady)
            
            # Ensure UI elements don't overlap
            self._prevent_element_overlap(scale_factor)
            
        except Exception as e:
            print(f"Error adjusting layout spacing: {str(e)}")
    
    def _prevent_element_overlap(self, scale_factor):
        """Prevent UI elements from overlapping at different resolutions."""
        try:
            # Adjust minimum sizes for frames to prevent overlap
            min_width = int(200 * scale_factor)
            min_height = int(100 * scale_factor)
            
            # Update main tab frames
            for widget in self.main_tab.winfo_children():
                if isinstance(widget, ttk.Frame):
                    # Set minimum size for frames
                    widget.grid_configure(minsize=(min_width, min_height))
                    
                    # Adjust child elements
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame):
                            child.grid_configure(padx=int(5 * scale_factor), pady=int(5 * scale_factor))
            
            # Update admin tab frames
            for widget in self.admin_tab.winfo_children():
                if isinstance(widget, ttk.Frame):
                    # Set minimum size for frames
                    widget.grid_configure(minsize=(min_width, min_height))
                    
                    # Adjust child elements
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame):
                            child.grid_configure(padx=int(5 * scale_factor), pady=int(5 * scale_factor))
            
            # Ensure receipt displays have proper minimum size
            if hasattr(self, 'receipt_text'):
                receipt_frame = self.receipt_text.master
                receipt_frame.grid_configure(minsize=(int(300 * scale_factor), int(200 * scale_factor)))
            
            if hasattr(self, 'model_text'):
                model_frame = self.model_text.master
                model_frame.grid_configure(minsize=(int(300 * scale_factor), int(200 * scale_factor)))
            
        except Exception as e:
            print(f"Error preventing element overlap: {str(e)}")
    
    def _adjust_window_size(self, width, height):
        """Adjust window size to ensure it fits within screen bounds and doesn't hide below taskbar."""
        try:
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Ensure window doesn't exceed screen dimensions
            if width > screen_width:
                width = screen_width - 20  # Leave a small margin
            
            # Ensure window doesn't hide below taskbar
            max_height = screen_height - self.taskbar_height - 20  # Leave margin for taskbar
            if height > max_height:
                height = max_height
            
            # Apply the adjusted window size
            self.root.geometry(f"{width}x{height}")
            
            # Center the window on screen, ensuring it doesn't go below taskbar
            x = (screen_width - width) // 2
            y = (screen_height - height - self.taskbar_height) // 2
            
            # Ensure y position is not negative (window above screen)
            y = max(0, y)
            
            self.root.geometry(f"+{x}+{y}")
            
            # Set window to be always on top temporarily to ensure it's visible
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            
        except Exception as e:
            print(f"Error adjusting window size: {str(e)}")
    
    def _scale_receipt_content(self, scale_factor):
        """Scale receipt text content based on scale factor."""
        try:
            # Get current receipt content if it exists
            if hasattr(self, 'current_input_data') and hasattr(self, 'current_result_data') and self.current_input_data and self.current_result_data:
                # Regenerate receipt with scaled formatting
                self._display_receipts(self.current_input_data, self.current_result_data)
                
                # Adjust font size in receipt text widget
                base_font_size = 10
                new_font_size = max(8, int(base_font_size * scale_factor))
                receipt_font = ('Courier New', new_font_size)  # Use monospace font for better alignment
                
                # Apply font to receipt text widgets
                self.receipt_text.config(font=receipt_font)
                self.model_text.config(font=receipt_font)
        except Exception as e:
            print(f"Error scaling receipt content: {str(e)}")
    
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
        """Display calculation results in both receipt text areas."""
        # Generate full receipt for display
        full_receipt = self._generate_full_receipt(input_data, result_data)
        self.receipt_text.delete(1.0, tk.END)
        self.receipt_text.insert(1.0, full_receipt)
        
        # Generate model screenshot for payment confirmation
        model_receipt = self._generate_model_receipt(input_data, result_data)
        self.model_text.delete(1.0, tk.END)
        self.model_text.insert(1.0, model_receipt)
    
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
        
        # Build fines section: omit entirely when fines are not shown
        if result_data.get('show_fines', True):
            fines_display = result_data.get('fines_display', '')
            fines_section = f"\nFINES:\n  {fines_display}\n"
        else:
            fines_section = ""
        
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
{advances_display}  Total: {format_currency_cop(result_data.get('advances_total', 0))}{fines_section}
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
    
    def _generate_model_receipt(self, input_data: dict, result_data: dict) -> str:
        """Generate model receipt text for payment confirmation in a compact, legacy-friendly format.

        Produces an organized layout suitable for both validation screenshots and
        the compact 'model screenshot' used in the app. Rules applied:
          - Header is centered.
          - Advances section is omitted if there are no advances with amount > 0.
          - Fines are omitted when show_fines is False (home worker).
          - Missing or zero-value fields produce empty/blank lines so layout remains stable.
        """
        # Width used for centering header in monospace output
        width = 38
        header_lines = [
            "BROADSPEC".center(width),
            "Payment Summary".center(width)
        ]
        separator = "-" * width

        # Safe converters
        def safe_float(v, default=0.0):
            try:
                return float(v)
            except Exception:
                return default

        def safe_int(v, default=0):
            try:
                return int(v)
            except Exception:
                return default

        # Extract core fields with safe defaults
        date = result_data.get('date', '')
        model_id = input_data.get('model_id', '') or ''
        model_name = input_data.get('model_name', '') or ''
        trm_official = format_currency_cop(safe_float(input_data.get('trm_official_cop', 0)))
        trm_broadspec = format_currency_cop(safe_float(result_data.get('trm_broadspec_cop', 0)))
        tokens = f"{safe_int(input_data.get('tokens', 0)):,}"
        percentage = input_data.get('percentage', 0)

        # Other sites: include only entries with amount > 0, show USD or TKS accordingly
        other_sites_lines = []
        for i, site in enumerate(input_data.get('other_sites', []), start=2):
            amt = safe_float(site.get('amount', 0))
            if amt <= 0:
                continue
            if site.get('site_type') == 'USD':
                other_sites_lines.append(f"  Site {i}: {format_currency_usd(amt)}")
            else:
                other_sites_lines.append(f"  Site {i}: {int(amt):,} TKS")

        # Advances: include only advances with amount > 0
        advances_lines = []
        for adv in input_data.get('advances', []):
            amt = safe_float(adv.get('amount', 0))
            if amt > 0:
                adv_date = adv.get('date', '')
                advances_lines.append(f"  {adv_date}: {format_currency_cop(amt)}")

        # Build ordered receipt lines to match the provided example
        parts = []
        parts.extend(header_lines)
        parts.append("")  # blank line
        parts.append(separator)
        parts.append(f"Date: {date}")
        parts.append("")  # blank
        parts.append(f"ID: {model_id}")
        parts.append("")  # blank
        parts.append(f"Model: {model_name}")
        parts.append("")  # blank
        parts.append(f"TRM Official: {trm_official}")
        parts.append(f"TRM BroadSpec: {trm_broadspec}")
        parts.append("")  # blank
        parts.append(f"Tokens: {tokens}")
        parts.append("")  # blank
        parts.append("Other Sites:")
        # leave a blank line under Other Sites to match the visual example
        if other_sites_lines:
            parts.append("")  # blank
            parts.extend(other_sites_lines)
        else:
            parts.append("")  # blank to indicate empty area

        parts.append("")  # blank
        parts.append(f"Percentage: {percentage:.0%}")

        # Only include Advances section if there are any positive advances
        if advances_lines:
            parts.append("")  # blank
            parts.append("Advances:")
            parts.extend(advances_lines)

        # Fines: show only when allowed
        if result_data.get('show_fines', True):
            parts.append("")  # blank
            parts.append(f"Fines: {format_currency_cop(safe_float(result_data.get('fines_total', 0)))}")

        parts.append("")  # blank
        parts.append("Total Payment:")
        parts.append(f"{format_currency_cop(safe_float(result_data.get('total_cop', 0)))}")
        parts.append("")  # blank
        parts.append(separator)

        # Return with leading/trailing newlines for consistent spacing in the text widget
        return "\n" + "\n".join(parts) + "\n"

    
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
    
    # PDF Preview methods
    
    def browse_pdf(self):
        """Browse for a PDF file."""
        filepath = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filepath:
            self.pdf_path_var.set(filepath)
    
    def load_pdf(self):
        """Load the selected PDF file."""
        pdf_path = self.pdf_path_var.get().strip()
        if not pdf_path:
            messagebox.showwarning("No File", "Please select a PDF file")
            return
        
        if not os.path.exists(pdf_path):
            messagebox.showerror("File Not Found", f"The file {pdf_path} does not exist")
            return
        
        if self.pdf_previewer.open_pdf(pdf_path):
            self.update_pdf_display()
            messagebox.showinfo("Success", "PDF loaded successfully")
        else:
            messagebox.showerror("Error", "Failed to load PDF file")
    
    def update_pdf_display(self):
        """Update the PDF display with the current page."""
        if not self.pdf_previewer.current_doc:
            return
        
        # Update page counter
        current_page = self.pdf_previewer.get_current_page() + 1  # Convert to 1-indexed
        total_pages = self.pdf_previewer.get_page_count()
        self.page_var.set(f"{current_page} / {total_pages}")
        
        # Get current zoom level
        zoom_str = self.zoom_var.get()
        zoom = float(zoom_str.rstrip('%')) / 100.0
        self.pdf_previewer.set_zoom(zoom)
        
        # Get page image
        tk_image = self.pdf_previewer.get_page_tk_image()
        if tk_image:
            # Clear canvas
            self.pdf_canvas.delete("all")
            
            # Store reference to prevent garbage collection
            self.current_pdf_image = tk_image
            
            # Calculate position to center image
            canvas_width = self.pdf_canvas.winfo_width()
            canvas_height = self.pdf_canvas.winfo_height()
            
            # If canvas hasn't been rendered yet, use default size
            if canvas_width <= 1:
                canvas_width = 800
            if canvas_height <= 1:
                canvas_height = 600
            
            img_width = tk_image.width()
            img_height = tk_image.height()
            
            # Calculate scroll region
            self.pdf_canvas.configure(scrollregion=(0, 0, img_width, img_height))
            
            # Place image at top-left of canvas
            self.pdf_canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    
    def prev_page(self):
        """Go to the previous page."""
        if not self.pdf_previewer.current_doc:
            return
        
        current_page = self.pdf_previewer.get_current_page()
        if current_page > 0:
            self.pdf_previewer.set_current_page(current_page - 1)
            self.update_pdf_display()
    
    def next_page(self):
        """Go to the next page."""
        if not self.pdf_previewer.current_doc:
            return
        
        current_page = self.pdf_previewer.get_current_page()
        total_pages = self.pdf_previewer.get_page_count()
        if current_page < total_pages - 1:
            self.pdf_previewer.set_current_page(current_page + 1)
            self.update_pdf_display()
    
    def on_zoom_change(self, event):
        """Handle zoom level change."""
        if not self.pdf_previewer.current_doc:
            return
        
        zoom_str = self.zoom_var.get()
        zoom = float(zoom_str.rstrip('%')) / 100.0
        self.pdf_previewer.set_zoom(zoom)
        self.update_pdf_display()
    
    def preview_last_pdf(self):
        """Preview the last generated PDF receipt."""
        if not self.current_input_data or not self.current_result_data:
            messagebox.showwarning("No Data", "Please calculate first before previewing")
            return
        
        try:
            # Generate the PDF to a temporary file for preview
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate the PDF using the controller
            self.controller.generate_receipt_pdf(self.current_input_data, self.current_result_data, temp_path)
            
            # Load PDF in admin tab for preview
            self.admin_pdf_path_var = tk.StringVar(value=f"Preview: {self.current_input_data.get('model_name', 'Unknown')}")
            if self.pdf_previewer.open_pdf(temp_path):
                self.admin_update_pdf_display()
                # Switch to admin tab to show preview
                self.notebook.select(self.admin_tab)
                messagebox.showinfo("Success", "PDF generated and loaded for preview")
            else:
                messagebox.showerror("Error", "Failed to load PDF for preview")
                
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to preview PDF: {str(e)}")

    
    # Admin PDF Preview methods
    
    def admin_browse_pdf(self):
        """Browse for a PDF file in admin tab."""
        filepath = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filepath:
            self.admin_pdf_path_var.set(filepath)
    
    def admin_load_pdf(self):
        """Load selected PDF file in admin tab."""
        pdf_path = self.admin_pdf_path_var.get().strip()
        if not pdf_path:
            messagebox.showwarning("No File", "Please select a PDF file")
            return
        
        if not os.path.exists(pdf_path):
            messagebox.showerror("File Not Found", f"The file {pdf_path} does not exist")
            return
        
        if self.pdf_previewer.open_pdf(pdf_path):
            self.admin_update_pdf_display()
            messagebox.showinfo("Success", "PDF loaded successfully")
        else:
            messagebox.showerror("Error", "Failed to load PDF file")
    
    def admin_update_pdf_display(self):
        """Update PDF display in admin tab with current page."""
        if not self.pdf_previewer.current_doc:
            return
        
        # Update page counter
        current_page = self.pdf_previewer.get_current_page() + 1  # Convert to 1-indexed
        total_pages = self.pdf_previewer.get_page_count()
        self.admin_page_var.set(f"{current_page} / {total_pages}")
        
        # Get current zoom level
        zoom_str = self.admin_zoom_var.get()
        zoom = float(zoom_str.rstrip('%')) / 100.0
        self.pdf_previewer.set_zoom(zoom)
        
        # Get page image
        tk_image = self.pdf_previewer.get_page_tk_image()
        if tk_image:
            # Clear canvas
            self.admin_pdf_canvas.delete("all")
            
            # Store reference to prevent garbage collection
            self.admin_current_pdf_image = tk_image
            
            # Calculate position to center image
            canvas_width = self.admin_pdf_canvas.winfo_width()
            canvas_height = self.admin_pdf_canvas.winfo_height()
            
            # If canvas hasn't been rendered yet, use default size
            if canvas_width <= 1:
                canvas_width = 600
            if canvas_height <= 1:
                canvas_height = 400
            
            img_width = tk_image.width()
            img_height = tk_image.height()
            
            # Calculate scroll region
            self.admin_pdf_canvas.configure(scrollregion=(0, 0, img_width, img_height))
            
            # Place image at top-left of canvas
            self.admin_pdf_canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    
    def admin_prev_page(self):
        """Go to previous page in admin tab."""
        if not self.pdf_previewer.current_doc:
            return
        
        current_page = self.pdf_previewer.get_current_page()
        if current_page > 0:
            self.pdf_previewer.set_current_page(current_page - 1)
            self.admin_update_pdf_display()
    
    def admin_next_page(self):
        """Go to next page in admin tab."""
        if not self.pdf_previewer.current_doc:
            return
        
        current_page = self.pdf_previewer.get_current_page()
        total_pages = self.pdf_previewer.get_page_count()
        if current_page < total_pages - 1:
            self.pdf_previewer.set_current_page(current_page + 1)
            self.admin_update_pdf_display()
    
    def admin_on_zoom_change(self, event):
        """Handle zoom level change in admin tab."""
        if not self.pdf_previewer.current_doc:
            return
        
        zoom_str = self.admin_zoom_var.get()
        zoom = float(zoom_str.rstrip('%')) / 100.0
        self.pdf_previewer.set_zoom(zoom)
        self.admin_update_pdf_display()
    
    def on_vault_double_click(self, event):
        """Handle double-click on vault item to preview PDF"""
        selected_indices = self.vault_listbox.curselection()
        if not selected_indices:
            return
        
        selected_index = selected_indices[0]
        
        # Get vault entry data
        if selected_index >= len(self.vault_entries):
            return
            
        entry = self.vault_entries[selected_index]
        vault_filename = entry.get('vault_filename')
        
        if not vault_filename:
            messagebox.showerror("Error", "No vault filename found for selected entry")
            return
        
        try:
            # Create temporary file for preview
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Retrieve file from vault
            file_bytes = self.controller.vault_repository.retrieve_file(vault_filename)
            
            # Write to temporary file
            with open(temp_path, 'wb') as f:
                f.write(file_bytes)
            
                        # Load PDF in admin tab
            self.admin_pdf_path_var = tk.StringVar(value=f"Vault: {vault_filename}")
            if self.pdf_previewer.open_pdf(temp_path):
                self.admin_update_pdf_display()
                # Switch to admin tab
                self.notebook.select(self.admin_tab)
            else:
                messagebox.showerror("Error", "Failed to load PDF for preview")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview PDF from vault: {str(e)}")