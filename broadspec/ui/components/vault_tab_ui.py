import os
import tkinter as tk
from tkinter import ttk, messagebox


class VaultTabUI:
    """Handles creation and management of the vault tab for vault management."""
    
    def __init__(self, parent_tab, window_setup, controller):
        """Initialize vault tab UI."""
        self.parent_tab = parent_tab
        self.window_setup = window_setup
        self.controller = controller
        
        self._create_vault_tab()
    
    def _create_vault_tab(self):
        """Create the vault tab for vault management."""
        vault_container = ttk.Frame(self.parent_tab, padding="10")
        vault_container.pack(fill=tk.BOTH, expand=True)
        
        if not self.controller.vault_repository:
            no_vault_label = ttk.Label(
                vault_container,
                text="Vault features are not available (cryptography package missing)",
                font=('Arial', 12)
            )
            no_vault_label.pack(pady=50)
            return
        
        vault_frame = ttk.LabelFrame(vault_container, text="Encrypted Vault (Vault)", padding="10")
        vault_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.vault_listbox = tk.Listbox(vault_frame, width=100, height=20, selectmode=tk.EXTENDED)
        self.vault_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vault_listbox.bind('<Double-Button-1>', self.on_double_click)
        
        scrollbar = ttk.Scrollbar(vault_frame, orient=tk.VERTICAL, command=self.vault_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vault_listbox['yscrollcommand'] = scrollbar.set
        
        btn_frame = ttk.Frame(vault_container)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        export_btn = ttk.Button(btn_frame, text="Export Selected", command=self.export_selected)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        import_btn = ttk.Button(btn_frame, text="Import PDFs", command=self.import_pdfs)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_vault)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.resolution_var = tk.StringVar(value="1920x1080")
        resolution_btn = ttk.Button(btn_frame, text="Toggle Resolution", command=self.toggle_resolution)
        resolution_btn.pack(side=tk.LEFT, padx=5)
        
        self.resolution_label = ttk.Label(btn_frame, textvariable=self.resolution_var)
        self.resolution_label.pack(side=tk.LEFT, padx=5)
        
        stats_frame = ttk.Frame(vault_container)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.vault_count_label = ttk.Label(stats_frame, text="Entries: 0")
        self.vault_count_label.pack(side=tk.LEFT, padx=(0,10))
        
        self.vault_size_label = ttk.Label(stats_frame, text="Vault size: 0 B")
        self.vault_size_label.pack(side=tk.LEFT)
        
        self.refresh_vault()
        
        self._create_pdf_preview_in_vault()
    
    def _create_pdf_preview_in_vault(self):
        """Create PDF preview section in vault tab."""
        if not self.window_setup.pdf_previewer.is_enabled():
            no_preview_label = ttk.Label(
                self.parent_tab,
                text="PDF Preview is disabled in configuration",
                font=('Arial', 10)
            )
            no_preview_label.pack(pady=10)
            return
        
        pdf_preview_frame = ttk.LabelFrame(self.parent_tab, text="PDF Preview", padding="10")
        pdf_preview_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            pdf_preview_frame.rowconfigure(1, weight=1)
            pdf_preview_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        canvas_frame = ttk.Frame(pdf_preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            canvas_frame.rowconfigure(0, weight=1)
            canvas_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        self.vault_pdf_canvas = tk.Canvas(canvas_frame, bg="white", width=600, height=400)
        vault_pdf_v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.vault_pdf_canvas.yview)
        vault_pdf_h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.vault_pdf_canvas.xview)
        
        self.vault_pdf_canvas.configure(yscrollcommand=vault_pdf_v_scrollbar.set, xscrollcommand=vault_pdf_h_scrollbar.set)
        
        self.vault_pdf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vault_pdf_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        vault_pdf_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        nav_frame = ttk.Frame(pdf_preview_frame)
        nav_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(nav_frame, text="Previous", command=self.prev_page).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="Next", command=self.next_page).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(nav_frame, text="Page:").pack(side=tk.LEFT, padx=(10, 2))
        self.vault_page_var = tk.StringVar(value="0 / 0")
        ttk.Label(nav_frame, textvariable=self.vault_page_var).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(nav_frame, text="Zoom:").pack(side=tk.LEFT, padx=(10, 2))
        self.vault_zoom_var = tk.StringVar(value="100%")
        vault_zoom_combo = ttk.Combobox(nav_frame, textvariable=self.vault_zoom_var, width=8, state='readonly')
        vault_zoom_combo['values'] = ('50%', '75%', '100%', '125%', '150%', '200%')
        vault_zoom_combo.current(2)
        vault_zoom_combo.bind('<<ComboboxSelected>>', self.vault_on_zoom_change)
        vault_zoom_combo.pack(side=tk.LEFT)
        
        self.vault_current_pdf_image = None
    
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
                filepath = tk.filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
                )
                if not filepath:
                    return
            else:
                directory = tk.filedialog.askdirectory(title="Select export directory")
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
            
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete: {str(e)}")
    
    def import_pdfs(self):
        """Import PDF files to vault."""
        if not self.controller.vault_repository:
            return
        
        filepaths = tk.filedialog.askopenfilenames(
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
        
        adjusted_height = new_height - self.window_setup.taskbar_height
        
        self._update_ui_for_resolution(new_width, adjusted_height)
    
    def _update_ui_for_resolution(self, width, height):
        """Update UI elements to fit the specified resolution."""
        pass
    
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
    
    # PDF Preview methods for vault tab
    def browse_pdf(self):
        """Browse for a PDF file in vault tab."""
        filepath = tk.filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filepath:
            self.vault_pdf_path_var.set(filepath)
    
    def load_pdf(self):
        """Load selected PDF file in vault tab."""
        pdf_path = self.vault_pdf_path_var.get().strip()
        if not pdf_path:
            messagebox.showwarning("No File", "Please select a PDF file")
            return
        
        if not os.path.exists(pdf_path):
            messagebox.showerror("File Not Found", f"The file {pdf_path} does not exist")
            return
        
        if self.window_setup.pdf_previewer.open_pdf(pdf_path):
            self.update_pdf_display()
            messagebox.showinfo("Success", "PDF loaded successfully")
        else:
            messagebox.showerror("Error", "Failed to load PDF file")
    
    def update_pdf_display(self):
        """Update PDF display in vault tab with current page."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        current_page = self.window_setup.pdf_previewer.get_current_page() + 1
        total_pages = self.window_setup.pdf_previewer.get_page_count()
        self.vault_page_var.set(f"{current_page} / {total_pages}")
        
        zoom_str = self.vault_zoom_var.get()
        zoom = float(zoom_str.rstrip('%')) / 100.0
        self.window_setup.pdf_previewer.set_zoom(zoom)
        
        tk_image = self.window_setup.pdf_previewer.get_page_tk_image()
        if tk_image:
            self.vault_pdf_canvas.delete("all")
            
            self.vault_current_pdf_image = tk_image
            
            canvas_width = self.vault_pdf_canvas.winfo_width()
            canvas_height = self.vault_pdf_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 600
            if canvas_height <= 1:
                canvas_height = 400
            
            img_width = tk_image.width()
            img_height = tk_image.height()
            
            self.vault_pdf_canvas.configure(scrollregion=(0, 0, img_width, img_height))
            
            self.vault_pdf_canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    
    def prev_page(self):
        """Go to previous page in vault tab."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        current_page = self.window_setup.pdf_previewer.get_current_page()
        if current_page > 0:
            self.window_setup.pdf_previewer.set_current_page(current_page - 1)
            self.update_pdf_display()
    
    def next_page(self):
        """Go to next page in vault tab."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        current_page = self.window_setup.pdf_previewer.get_current_page()
        total_pages = self.window_setup.pdf_previewer.get_page_count()
        if current_page < total_pages - 1:
            self.window_setup.pdf_previewer.set_current_page(current_page + 1)
            self.update_pdf_display()
    
    def vault_on_zoom_change(self, event):
        """Handle zoom level change in vault tab."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        zoom_str = self.vault_zoom_var.get()
        zoom = float(zoom_str.rstrip('%')) / 100.0
        self.window_setup.pdf_previewer.set_zoom(zoom)
        self.update_pdf_display()
    
    def on_double_click(self, event):
        """Handle double-click on vault item to preview PDF"""
        selected_indices = self.vault_listbox.curselection()
        if not selected_indices:
            return
        
        selected_index = selected_indices[0]
        
        if selected_index >= len(self.vault_entries):
            return
            
        entry = self.vault_entries[selected_index]
        vault_filename = entry.get('vault_filename')
        
        if not vault_filename:
            messagebox.showerror("Error", "No vault filename found for selected entry")
            return
        
        try:
            file_bytes = self.controller.vault_repository.retrieve_file(vault_filename)
            
            self.vault_pdf_path_var = tk.StringVar(value=f"Vault: {vault_filename}")
            if self.window_setup.pdf_previewer.open_pdf_bytes(file_bytes):
                self.update_pdf_display()
                self.window_setup.notebook.select(self.parent_tab)
            else:
                messagebox.showerror("Error", "Failed to load PDF for preview")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview PDF from vault: {str(e)}")