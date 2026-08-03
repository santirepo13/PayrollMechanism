"""
Handles creation and management of the admin calculator tab.
"""

import tkinter as tk
from tkinter import ttk, messagebox

class AdminTabUI:
    def __init__(self, parent_tab, window_setup):
        """Initialize admin tab UI."""
        self.parent_tab = parent_tab
        self.window_setup = window_setup
        
        self._create_admin_tab()

    def _create_admin_tab(self):
        """Create and configure the admin tab UI layout."""
        try:
            # Main container with proper padding
            main_frame = ttk.Frame(self.parent_tab, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Title
            title = ttk.Label(main_frame, text="COP to USD Calculator", font=('Arial', 16, 'bold'))
            title.grid(row=0, column=0, columnspan=5, pady=(0, 15))

            # Input frame
            input_frame = ttk.LabelFrame(main_frame, text="Input Values")
            input_frame.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), padx=5)

            # Fee Breakdown frame
            notes_frame = ttk.LabelFrame(main_frame, text="Fee Breakdown")
            notes_frame.grid(row=4, column=0, columnspan=5, sticky=(tk.W, tk.E), padx=5, pady=5)

            # Create input fields
            row = 0

            trm_official_label = ttk.Label(input_frame, text="TRM Official $COP (NOT NULL):", font=('Arial', 10))
            trm_official_label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            self.trm_official_cop = ttk.Entry(input_frame)
            self.trm_official_cop.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
            self.trm_official_cop.insert(0, "0")
            row += 1

            btk_trm_label = ttk.Label(input_frame, text="BTK TRM $COP:", font=('Arial', 10))
            btk_trm_label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            self.btk_trm_cop = ttk.Entry(input_frame)
            self.btk_trm_cop.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
            self.btk_trm_cop.insert(0, "0")
            row += 1

            target_cop_label = ttk.Label(input_frame, text="Desired COP Amount (COP):", font=('Arial', 10))
            target_cop_label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            self.target_cop = ttk.Entry(input_frame)
            self.target_cop.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
            self.target_cop.insert(0, "0")
            # Fees display
            fee_notes = tk.Text(notes_frame, wrap=tk.WORD, height=4, width=60,
                               font=('Arial', 10), state=tk.NORMAL)
            fee_notes.insert("1.0",
                "Fees Breakdown:\n"
                "\n"
                "• 4% Retention Tax on Original USD\n"
                "• Transfer Fee: USD 6.99 + Taxes\n"
                )
            fee_notes.config(state=tk.DISABLED)
            fee_notes.grid(row=0, column=0, columnspan=5, sticky=tk.W, padx=5, pady=5)

            # Add calculation and exit buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=5, column=0, columnspan=5, sticky=(tk.E), padx=5, pady=10)

            calculate_button = ttk.Button(button_frame, text="Calculate Required USD",
                                         command=self._calculate_usd_amount)
            calculate_button.pack(side=tk.LEFT, padx=5)

            exit_button = ttk.Button(button_frame, text="Exit", command=self._exit_calculator)
            exit_button.pack(side=tk.LEFT, padx=5)

            # Results frame
            results_frame = ttk.LabelFrame(main_frame, text="Required Amount Calculations")
            results_frame.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E), padx=5, pady=10)

            self.usd_needed_label = ttk.Label(results_frame, text="Required USD:", font=('Arial', 12, 'bold'))
            self.usd_needed_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

            self.total_usd = ttk.Label(results_frame, text="", font=('Arial', 12, 'bold'))
            self.total_usd.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

            self.subframe = ttk.Frame(results_frame)
            self.subframe.grid(row=1, column=0, columnspan=5, padx=10, pady=10)

            # Setup widgets for fee breakdown
            self.retention_tax_label = ttk.Label(self.subframe, text="Retention Tax:", font=('Arial', 10, 'bold'))
            self.retention_tax_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

            self.retention_tax = ttk.Label(self.subframe, text="", font=('Arial', 10))
            self.retention_tax.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

            self.transfer_fee_label = ttk.Label(self.subframe, text="Transfer Fee (including tax):",
                                               font=('Arial', 10, 'bold'))
            self.transfer_fee_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

            self.transfer_fee = ttk.Label(self.subframe, text="", font=('Arial', 10))
            self.transfer_fee.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        except Exception as e:
            print(f"Error creating admin tab: {e}")

    def _calculate_usd_amount(self):
        """Compute required gross USD to reach desired COP after 4% retention and transfer fee."""
        try:
            trm_official = float((self.trm_official_cop.get() or "0").replace(",", ""))
            btk_trm = float((self.btk_trm_cop.get() or "0").replace(",", ""))
            desired_cop = float((self.target_cop.get() or "0").replace(",", ""))

            if trm_official <= 0 or btk_trm <= 0 or desired_cop <= 0:
                raise ValueError("Inputs must be greater than 0")

            cfg = getattr(self.window_setup, 'config', {}) or {}
            app_cfg = cfg.get('app', {})
            calc_cfg = cfg.get('calculation', {})

            base_fee = float(app_cfg.get('transfer_cost', 6.99))
            fee_tax = float(calc_cfg.get('transfer_cost_tax', 0.19))
            retention_pct = float(calc_cfg.get('retention_tax_percent', 0.04)) if 'retention_tax_percent' in calc_cfg else 0.04

            # Transfer fee in USD (6.99 + 19% VAT by default)
            transfer_fee_usd = base_fee * (1.0 + fee_tax)

            # Solve for gross USD so that (gross - retention - fee) * BTK_TRM = desired COP
            gross_usd = (desired_cop / btk_trm + transfer_fee_usd) / (1.0 - retention_pct)
            retention_usd = gross_usd * retention_pct

            # Update results
            self.total_usd.config(text=f"{gross_usd:,.2f} USD")
            self.retention_tax.config(text=f"{retention_usd:,.2f} USD ({retention_usd * btk_trm:,.0f} COP)")
            self.transfer_fee.config(text=f"{transfer_fee_usd:,.2f} USD ({transfer_fee_usd * btk_trm:,.0f} COP)")
        except Exception as e:
            self.total_usd.config(text="Invalid input")
            self.retention_tax.config(text="")
            self.transfer_fee.config(text="")
            try:
                messagebox.showerror("Invalid input", "Please enter positive numbers for TRM Official, BTK TRM and Desired COP.")
            except Exception:
                pass

    def _exit_calculator(self):
        """Handle exit from admin tab."""
        print("Exiting admin calculator")