import tkinter as tk
from tkinter import ttk


class ResolutionManager:
    """Handles UI resolution management and scaling."""
    
    def __init__(self, window_setup, admin_tab_ui):
        """Initialize resolution manager."""
        self.window_setup = window_setup
        self.admin_tab_ui = admin_tab_ui
        
        if hasattr(self.admin_tab_ui, 'toggle_resolution'):
            self.admin_tab_ui.toggle_resolution = self.toggle_resolution
            self.admin_tab_ui._update_ui_for_resolution = self._update_ui_for_resolution
    
    def toggle_resolution(self):
        """Toggle between 1920x1080 and 1366x768 resolutions."""
        current_resolution = self.admin_tab_ui.resolution_var.get()
        
        if current_resolution == "1920x1080":
            self.admin_tab_ui.resolution_var.set("1366x768")
            new_width, new_height = 1366, 768
        else:
            self.admin_tab_ui.resolution_var.set("1920x1080")
            new_width, new_height = 1920, 1080
        
        adjusted_height = new_height - self.window_setup.taskbar_height
        
        self._update_ui_for_resolution(new_width, adjusted_height)
    
    def _update_ui_for_resolution(self, width, height):
        """Update UI elements to fit specified resolution."""
        scale_factor_width = width / 1920
        scale_factor_height = height / (1080 - self.window_setup.taskbar_height)
        
        scale_factor = min(scale_factor_width, scale_factor_height)
        
        self.current_scale_factor = scale_factor
        
        self._scale_ui_elements(scale_factor)
        
        self._adjust_layout_spacing(scale_factor)
        
        self._adjust_window_size(width, height)
        
        self._scale_receipt_content(scale_factor)
    
    def _scale_ui_elements(self, scale_factor):
        """Scale UI elements based on scale factor."""
        base_font_size = 10
        new_font_size = max(8, int(base_font_size * scale_factor))
        
        title_font = ('Arial', max(14, int(16 * scale_factor)), 'bold')
        
        input_font = ('Arial', new_font_size)
        
        try:
            for widget in self.window_setup.main_tab.winfo_children():
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
                            child.config(font=input_font)
                            for frame_child in child.winfo_children():
                                if isinstance(frame_child, ttk.Label):
                                    frame_child.config(font=input_font)
                                elif isinstance(frame_child, tk.Text):
                                    frame_child.config(font=('Courier New', new_font_size))
            
            for widget in self.window_setup.admin_tab.winfo_children():
                if isinstance(widget, ttk.Label):
                    widget.config(font=input_font)
                elif isinstance(widget, ttk.Button):
                    widget.config(font=input_font)
                elif isinstance(widget, tk.Listbox):
                    widget.config(font=input_font)
                elif isinstance(widget, ttk.LabelFrame):
                    widget.config(font=input_font)
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
                            canvas_width = int(600 * scale_factor)
                            canvas_height = int(400 * scale_factor)
                            frame_child.config(width=canvas_width, height=canvas_height)
            
            style = ttk.Style()
            style.configure('TNotebook.Tab', font=input_font)
            
        except Exception as e:
            print(f"Error scaling UI elements: {str(e)}")
    
    def _adjust_layout_spacing(self, scale_factor):
        """Adjust padding and spacing based on scale factor."""
        try:
            base_padding = 10
            scaled_padding = max(5, int(base_padding * scale_factor))
            
            self.window_setup.main_frame.config(padding=scaled_padding)
            
            self.window_setup.notebook.config(padding=scaled_padding)
            
            for tab in [self.window_setup.main_tab, self.window_setup.admin_tab]:
                for widget in tab.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        widget.config(padding=scaled_padding)
                    elif isinstance(widget, ttk.LabelFrame):
                        widget.config(padding=scaled_padding)
            
            for tab in [self.window_setup.main_tab, self.window_setup.admin_tab]:
                for widget in tab.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Frame):
                                for btn in child.winfo_children():
                                    if isinstance(btn, ttk.Button):
                                        padx = max(2, int(5 * scale_factor))
                                        pady = max(2, int(5 * scale_factor))
                                        btn.grid_configure(padx=padx, pady=pady)
            
            self._prevent_element_overlap(scale_factor)
            
        except Exception as e:
            print(f"Error adjusting layout spacing: {str(e)}")
    
    def _prevent_element_overlap(self, scale_factor):
        """Prevent UI elements from overlapping at different resolutions."""
        try:
            min_width = int(200 * scale_factor)
            min_height = int(100 * scale_factor)
            
            for widget in self.window_setup.main_tab.winfo_children():
                if isinstance(widget, ttk.Frame):
                    widget.grid_configure(minsize=(min_width, min_height))
                    
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame):
                            child.grid_configure(padx=int(5 * scale_factor), pady=int(5 * scale_factor))
            
            for widget in self.window_setup.admin_tab.winfo_children():
                if isinstance(widget, ttk.Frame):
                    widget.grid_configure(minsize=(min_width, min_height))
                    
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame):
                            child.grid_configure(padx=int(5 * scale_factor), pady=int(5 * scale_factor))
            
            if hasattr(self.window_setup, 'receipt_text'):
                receipt_frame = self.window_setup.receipt_text.master
                receipt_frame.grid_configure(minsize=(int(300 * scale_factor), int(200 * scale_factor)))
            
            if hasattr(self.window_setup, 'model_text'):
                model_frame = self.window_setup.model_text.master
                model_frame.grid_configure(minsize=(int(300 * scale_factor), int(200 * scale_factor)))
            
        except Exception as e:
            print(f"Error preventing element overlap: {str(e)}")
    
    def _adjust_window_size(self, width, height):
        """Adjust window size to ensure it fits within screen bounds and doesn't hide below taskbar."""
        try:
            screen_width = self.window_setup.root.winfo_screenwidth()
            screen_height = self.window_setup.root.winfo_screenheight()
            
            if width > screen_width:
                width = screen_width - 20
            
            max_height = screen_height - self.window_setup.taskbar_height - 20
            if height > max_height:
                height = max_height
            
            self.window_setup.root.geometry(f"{width}x{height}")
            
            x = (screen_width - width) // 2
            y = (screen_height - height - self.window_setup.taskbar_height) // 2
            
            y = max(0, y)
            
            self.window_setup.root.geometry(f"+{x}+{y}")
            
            self.window_setup.root.attributes('-topmost', True)
            self.window_setup.root.after(100, lambda: self.window_setup.root.attributes('-topmost', False))
            
        except Exception as e:
            print(f"Error adjusting window size: {str(e)}")
    
    def _scale_receipt_content(self, scale_factor):
        """Scale receipt text content based on scale factor."""
        try:
            if (hasattr(self.window_setup, 'current_input_data') and 
                hasattr(self.window_setup, 'current_result_data') and 
                self.window_setup.current_input_data and 
                self.window_setup.current_result_data):
                pass
                
                base_font_size = 10
                new_font_size = max(8, int(base_font_size * scale_factor))
                receipt_font = ('Courier New', new_font_size)
                
                if hasattr(self.window_setup, 'receipt_text'):
                    self.window_setup.receipt_text.config(font=receipt_font)
                if hasattr(self.window_setup, 'model_text'):
                    self.window_setup.model_text.config(font=receipt_font)
        except Exception as e:
            print(f"Error scaling receipt content: {str(e)}")