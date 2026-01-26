import tkinter as tk
from tkinter import ttk
from datetime import datetime


class MainTabUI:
    """Handles creation and management of the main calculator tab."""
    
    def __init__(self, parent_tab, window_setup):
        """Initialize main tab UI."""
        self.parent_tab = parent_tab
        self.window_setup = window_setup
        
        self.advances_entries = []
        self.other_sites_entries = []
        
        self._create_main_tab()
    
    def _create_main_tab(self):
        """Create the main calculator tab."""
        main_frame = ttk.Frame(self.parent_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            self.parent_tab.rowconfigure(0, weight=1)
            self.parent_tab.columnconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=0, minsize=320)
            main_frame.columnconfigure(1, weight=3)
            main_frame.columnconfigure(2, weight=0)
            main_frame.rowconfigure(1, weight=1)
            main_frame.rowconfigure(2, weight=0)
        except Exception:
            pass
        
        title = ttk.Label(main_frame, text="BROADSPEC PAYMENT CALCULATOR",
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=(0, 10))
        
        try:
            input_frame.columnconfigure(0, weight=0)
            input_frame.columnconfigure(1, weight=1)
        except Exception:
            pass
        
        self._create_input_fields(input_frame)
        
        self._create_receipt_displays(main_frame)
        
        self.action_frame = ttk.Frame(main_frame)
        self.action_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.calculate_btn = ttk.Button(self.action_frame, text="Calculate")
        self.calculate_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.action_frame, text="Clear Fields", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        
        self.save_model_image_btn = ttk.Button(self.action_frame, text="Save Model Image")
        self.save_model_image_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_pdf_btn = ttk.Button(self.action_frame, text="Save PDF")
        self.save_pdf_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_input_fields(self, parent):
        """Create input field widgets."""
        row = 0
        
        ttk.Label(parent, text="Model ID #:", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.model_id = ttk.Entry(parent, width=20)
        self.model_id.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(parent, text="Model Name:", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.model_name = ttk.Entry(parent, width=20)
        self.model_name.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(parent, text="TRM Official $COP (NOT NULL):", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.trm_official_cop = ttk.Entry(parent, width=20)
        self.trm_official_cop.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(parent, text="BTK TRM $COP:", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.btk_trm_cop = ttk.Entry(parent, width=20)
        self.btk_trm_cop.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Checkbox to override the 200 COP deduction when tokens >= 3000
        # If enabled, TRM BroadSpec uses default adjustment (e.g., -300) regardless of tokens
        self.override_high_tokens_trm_var = tk.BooleanVar(value=False)
        self.override_high_tokens_trm_cb = ttk.Checkbutton(
            parent,
            text="Always apply -300 TRM (ignore 3000+ TKS rule)",
            variable=self.override_high_tokens_trm_var
        )
        self.override_high_tokens_trm_cb.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(parent, text="Tokens (TKS):", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tokens = ttk.Entry(parent, width=20)
        self.tokens.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(parent, text="Percentage:", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.percentage = ttk.Combobox(parent, width=17, state='readonly')
        self.percentage['values'] = ('60%', '70%', '75%')
        self.percentage.current(1)
        self.percentage.bind('<<ComboboxSelected>>', self.on_percentage_change)
        self.percentage.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(parent, text="Other Sites (USD or TKS):", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5,5))
        row += 1
        
        other_sites_frame = ttk.Frame(parent)
        other_sites_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.other_sites_list_frame = ttk.Frame(other_sites_frame)
        self.other_sites_list_frame.pack(fill='x')
        
        add_other_site_btn = ttk.Button(other_sites_frame, text="+ Add Other Site", command=self.add_other_site_field)
        add_other_site_btn.pack(pady=5)
        row += 1
        
        ttk.Label(parent, text="Previous Fortnight USD:", font=('Arial', 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.previous_fortnight_usd = ttk.Entry(parent, width=20)
        self.previous_fortnight_usd.insert(0, "0")
        self.previous_fortnight_usd.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(parent, text="Advances:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10,5))
        row += 1
        
        advances_frame = ttk.Frame(parent)
        advances_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.advances_list_frame = ttk.Frame(advances_frame)
        self.advances_list_frame.pack(fill='x')
        
        add_advance_btn = ttk.Button(advances_frame, text="+ Add Advance", command=self.add_advance_field)
        add_advance_btn.pack(pady=5)
        row += 1
        
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
        
        self.add_advance_field()
        self.add_other_site_field()
        self.on_percentage_change(None)
    
    def _create_receipt_displays(self, parent):
        """Create receipt display area with dual box layout (full receipt and model screenshot)."""
        receipt_container = ttk.Frame(parent)
        receipt_container.grid(row=1, column=1, columnspan=2, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        try:
            receipt_container.columnconfigure(0, weight=1)
            receipt_container.columnconfigure(1, weight=1)
            receipt_container.rowconfigure(0, weight=1)
        except Exception:
            pass
        
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
    
    def on_percentage_change(self, event):
        """Enable/disable fines based on percentage selection."""
        try:
            perc_str = self.percentage.get()
            percentage = float(perc_str.strip('%')) / 100
            
            if percentage > 0.60:
                self.fines_count.config(state='disabled')
                self.custom_fine_cop.config(state='disabled')
                self.fines_count.delete(0, tk.END)
                self.fines_count.insert(0, "0")
                self.custom_fine_cop.delete(0, tk.END)
                self.fines_label.config(text="Fines (Disabled - Home Worker)")
            else:
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
        
        self.other_sites_entries.append((site_type_cb, amount_entry, frame))
    
    def remove_other_site_field(self, frame):
        """Remove an other-site entry field."""
        for i, (type_cb, amount_e, f) in enumerate(self.other_sites_entries):
            if f == frame:
                self.other_sites_entries.pop(i)
                frame.destroy()
                break
        
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
        try:
            self.override_high_tokens_trm_var.set(False)
        except Exception:
            pass
        
        if hasattr(self, 'other_sites_entries'):
            for type_cb, amount_e, frame in self.other_sites_entries:
                frame.destroy()
            self.other_sites_entries = []
            self.add_other_site_field()
        
        for date_e, amount_e, frame in self.advances_entries:
            frame.destroy()
        self.advances_entries = []
        self.add_advance_field()
        
        self.fines_count.delete(0, tk.END)
        self.fines_count.insert(0, "0")
        self.custom_fine_cop.delete(0, tk.END)
        
        self.receipt_text.delete(1.0, tk.END)
        self.model_text.delete(1.0, tk.END)
        
        self.window_setup.current_input_data = None
        self.window_setup.current_result_data = None
        
        self.on_percentage_change(None)
