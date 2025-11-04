"""
PDF preview handler component for BroadSpec Payment Calculator.
"""
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import tempfile


class PDFPreviewHandler:
    """Handles PDF preview functionality."""
    
    def __init__(self, window_setup, admin_tab_ui, controller):
        """Initialize PDF preview handler."""
        self.window_setup = window_setup
        self.admin_tab_ui = admin_tab_ui
        self.controller = controller
        
        # Update the PDF preview methods in admin tab UI
        if hasattr(self.admin_tab_ui, 'admin_browse_pdf'):
            self.admin_tab_ui.admin_browse_pdf = self.admin_browse_pdf
        
        if hasattr(self.admin_tab_ui, 'admin_load_pdf'):
            self.admin_tab_ui.admin_load_pdf = self.admin_load_pdf
        
        if hasattr(self.admin_tab_ui, 'admin_update_pdf_display'):
            self.admin_tab_ui.admin_update_pdf_display = self.admin_update_pdf_display
        
        if hasattr(self.admin_tab_ui, 'admin_prev_page'):
            self.admin_tab_ui.admin_prev_page = self.admin_prev_page
        
        if hasattr(self.admin_tab_ui, 'admin_next_page'):
            self.admin_tab_ui.admin_next_page = self.admin_next_page
        
        if hasattr(self.admin_tab_ui, 'admin_on_zoom_change'):
            self.admin_tab_ui.admin_on_zoom_change = self.admin_on_zoom_change
        
        if hasattr(self.admin_tab_ui, 'on_vault_double_click'):
            self.admin_tab_ui.on_vault_double_click = self.on_vault_double_click
        
        # Add preview_last_pdf method to admin tab UI
        self.admin_tab_ui.preview_last_pdf = self.preview_last_pdf
        
        # Add main tab PDF preview methods
        self.admin_tab_ui.browse_pdf = self.browse_pdf
        self.admin_tab_ui.load_pdf = self.load_pdf
        self.admin_tab_ui.update_pdf_display = self.update_pdf_display
        self.admin_tab_ui.prev_page = self.prev_page
        self.admin_tab_ui.next_page = self.next_page
        self.admin_tab_ui.on_zoom_change = self.on_zoom_change
    
    def browse_pdf(self):
        """Browse for a PDF file."""
        filepath = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filepath:
            # Store path in admin tab for consistency
            if not hasattr(self.admin_tab_ui, 'pdf_path_var'):
                self.admin_tab_ui.pdf_path_var = tk.StringVar()
            self.admin_tab_ui.pdf_path_var.set(filepath)
    
    def load_pdf(self):
        """Load the selected PDF file."""
        pdf_path = None
        # Try to get path from admin tab first
        if hasattr(self.admin_tab_ui, 'pdf_path_var'):
            pdf_path = self.admin_tab_ui.pdf_path_var.get().strip()
        
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
        """Update the PDF display with the current page."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        # Update page counter
        current_page = self.window_setup.pdf_previewer.get_current_page() + 1  # Convert to 1-indexed
        total_pages = self.window_setup.pdf_previewer.get_page_count()
        
        # Update admin page var if available
        if hasattr(self.admin_tab_ui, 'admin_page_var'):
            self.admin_tab_ui.admin_page_var.set(f"{current_page} / {total_pages}")
        
        # Get current zoom level
        zoom_str = "100%"
        if hasattr(self.admin_tab_ui, 'admin_zoom_var'):
            zoom_str = self.admin_tab_ui.admin_zoom_var.get()
        zoom = float(zoom_str.rstrip('%')) / 100.0
        self.window_setup.pdf_previewer.set_zoom(zoom)
        
        # Get page image
        tk_image = self.window_setup.pdf_previewer.get_page_tk_image()
        if tk_image:
            # Clear canvas
            if hasattr(self.admin_tab_ui, 'admin_pdf_canvas'):
                self.admin_tab_ui.admin_pdf_canvas.delete("all")
                
                # Store reference to prevent garbage collection
                self.admin_tab_ui.admin_current_pdf_image = tk_image
                
                # Calculate position to center image
                canvas_width = self.admin_tab_ui.admin_pdf_canvas.winfo_width()
                canvas_height = self.admin_tab_ui.admin_pdf_canvas.winfo_height()
                
                # If canvas hasn't been rendered yet, use default size
                if canvas_width <= 1:
                    canvas_width = 600
                if canvas_height <= 1:
                    canvas_height = 400
                
                img_width = tk_image.width()
                img_height = tk_image.height()
                
                # Calculate scroll region
                self.admin_tab_ui.admin_pdf_canvas.configure(scrollregion=(0, 0, img_width, img_height))
                
                # Place image at top-left of canvas
                self.admin_tab_ui.admin_pdf_canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    
    def prev_page(self):
        """Go to the previous page."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        current_page = self.window_setup.pdf_previewer.get_current_page()
        if current_page > 0:
            self.window_setup.pdf_previewer.set_current_page(current_page - 1)
            self.update_pdf_display()
    
    def next_page(self):
        """Go to the next page."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        current_page = self.window_setup.pdf_previewer.get_current_page()
        total_pages = self.window_setup.pdf_previewer.get_page_count()
        if current_page < total_pages - 1:
            self.window_setup.pdf_previewer.set_current_page(current_page + 1)
            self.update_pdf_display()
    
    def on_zoom_change(self, event):
        """Handle zoom level change."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        zoom_str = "100%"
        if hasattr(self.admin_tab_ui, 'admin_zoom_var'):
            zoom_str = self.admin_tab_ui.admin_zoom_var.get()
        zoom = float(zoom_str.rstrip('%')) / 100.0
        self.window_setup.pdf_previewer.set_zoom(zoom)
        self.update_pdf_display()
    
    def admin_browse_pdf(self):
        """Browse for a PDF file in admin tab."""
        filepath = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filepath:
            self.admin_tab_ui.admin_pdf_path_var.set(filepath)
    
    def admin_load_pdf(self):
        """Load selected PDF file in admin tab."""
        pdf_path = self.admin_tab_ui.admin_pdf_path_var.get().strip()
        if not pdf_path:
            messagebox.showwarning("No File", "Please select a PDF file")
            return
        
        if not os.path.exists(pdf_path):
            messagebox.showerror("File Not Found", f"The file {pdf_path} does not exist")
            return
        
        if self.window_setup.pdf_previewer.open_pdf(pdf_path):
            self.admin_update_pdf_display()
            messagebox.showinfo("Success", "PDF loaded successfully")
        else:
            messagebox.showerror("Error", "Failed to load PDF file")
    
    def admin_update_pdf_display(self):
        """Update PDF display in admin tab with current page."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        # Update page counter
        current_page = self.window_setup.pdf_previewer.get_current_page() + 1  # Convert to 1-indexed
        total_pages = self.window_setup.pdf_previewer.get_page_count()
        self.admin_tab_ui.admin_page_var.set(f"{current_page} / {total_pages}")
        
        # Get current zoom level
        zoom_str = self.admin_tab_ui.admin_zoom_var.get()
        zoom = float(zoom_str.rstrip('%')) / 100.0
        self.window_setup.pdf_previewer.set_zoom(zoom)
        
        # Get page image
        tk_image = self.window_setup.pdf_previewer.get_page_tk_image()
        if tk_image:
            # Clear canvas
            self.admin_tab_ui.admin_pdf_canvas.delete("all")
            
            # Store reference to prevent garbage collection
            self.admin_tab_ui.admin_current_pdf_image = tk_image
            
            # Calculate position to center image
            canvas_width = self.admin_tab_ui.admin_pdf_canvas.winfo_width()
            canvas_height = self.admin_tab_ui.admin_pdf_canvas.winfo_height()
            
            # If canvas hasn't been rendered yet, use default size
            if canvas_width <= 1:
                canvas_width = 600
            if canvas_height <= 1:
                canvas_height = 400
            
            img_width = tk_image.width()
            img_height = tk_image.height()
            
            # Calculate scroll region
            self.admin_tab_ui.admin_pdf_canvas.configure(scrollregion=(0, 0, img_width, img_height))
            
            # Place image at top-left of canvas
            self.admin_tab_ui.admin_pdf_canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    
    def admin_prev_page(self):
        """Go to previous page in admin tab."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        current_page = self.window_setup.pdf_previewer.get_current_page()
        if current_page > 0:
            self.window_setup.pdf_previewer.set_current_page(current_page - 1)
            self.admin_update_pdf_display()
    
    def admin_next_page(self):
        """Go to next page in admin tab."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        current_page = self.window_setup.pdf_previewer.get_current_page()
        total_pages = self.window_setup.pdf_previewer.get_page_count()
        if current_page < total_pages - 1:
            self.window_setup.pdf_previewer.set_current_page(current_page + 1)
            self.admin_update_pdf_display()
    
    def admin_on_zoom_change(self, event):
        """Handle zoom level change in admin tab."""
        if not self.window_setup.pdf_previewer.current_doc:
            return
        
        zoom_str = self.admin_tab_ui.admin_zoom_var.get()
        zoom = float(zoom_str.rstrip('%')) / 100.0
        self.window_setup.pdf_previewer.set_zoom(zoom)
        self.admin_update_pdf_display()
    
    def on_vault_double_click(self, event):
        """Handle double-click on vault item to preview PDF"""
        selected_indices = self.admin_tab_ui.vault_listbox.curselection()
        if not selected_indices:
            return
        
        selected_index = selected_indices[0]
        
        # Get vault entry data
        if selected_index >= len(self.admin_tab_ui.vault_entries):
            return
            
        entry = self.admin_tab_ui.vault_entries[selected_index]
        vault_filename = entry.get('vault_filename')
        
        if not vault_filename:
            messagebox.showerror("Error", "No vault filename found for selected entry")
            return
        
        try:
            # Create temporary file for preview
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Retrieve file from vault
            file_bytes = self.controller.vault_repository.retrieve_file(vault_filename)
            
            # Write to temporary file
            with open(temp_path, 'wb') as f:
                f.write(file_bytes)
            
            # Load PDF in admin tab
            self.admin_tab_ui.admin_pdf_path_var = tk.StringVar(value=f"Vault: {vault_filename}")
            if self.window_setup.pdf_previewer.open_pdf(temp_path):
                self.admin_update_pdf_display()
                # Switch to admin tab
                self.window_setup.notebook.select(self.window_setup.admin_tab)
            else:
                messagebox.showerror("Error", "Failed to load PDF for preview")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview PDF from vault: {str(e)}")
    
    def preview_last_pdf(self):
        """Preview the last generated PDF receipt."""
        if not self.window_setup.current_input_data or not self.window_setup.current_result_data:
            messagebox.showwarning("No Data", "Please calculate first before previewing")
            return
        
        try:
            # Generate the PDF to a temporary file for preview
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate the PDF using the controller
            self.controller.generate_receipt_pdf(
                self.window_setup.current_input_data, 
                self.window_setup.current_result_data, 
                temp_path
            )
            
            # Load PDF in admin tab for preview
            self.admin_tab_ui.admin_pdf_path_var = tk.StringVar(
                value=f"Preview: {self.window_setup.current_input_data.get('model_name', 'Unknown')}"
            )
            if self.window_setup.pdf_previewer.open_pdf(temp_path):
                self.admin_update_pdf_display()
                # Switch to admin tab to show preview
                self.window_setup.notebook.select(self.window_setup.admin_tab)
                messagebox.showinfo("Success", "PDF generated and loaded for preview")
            else:
                messagebox.showerror("Error", "Failed to load PDF for preview")
                
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to preview PDF: {str(e)}")