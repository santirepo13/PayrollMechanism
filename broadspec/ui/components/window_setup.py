import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from broadspec.utils.pdf_preview import PDFPreviewer


class WindowSetup:
    """Handles window setup and initialization."""
    
    def __init__(self, root: tk.Tk, config: Dict[str, Any]):
        """Initialize window setup."""
        self.root = root
        self.config = config
        
        self.root.title("BroadSpec Payment Calculator")
        
        ui_config = config.get('ui', {})
        width = ui_config.get('default_width', 1900)
        height = ui_config.get('default_height', 1064)
        
        self.taskbar_height = 40
        adjusted_height = height - self.taskbar_height
        
        self.root.geometry(f"{width}x{adjusted_height}")
        self.root.resizable(True, True)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        try:
            self.root.rowconfigure(0, weight=1)
            self.root.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        try:
            self.main_frame.rowconfigure(0, weight=1)
            self.main_frame.columnconfigure(0, weight=1)
        except Exception:
            pass
        
        self.pdf_previewer = PDFPreviewer(config)
        
        self.notebook = ttk.Notebook(self.main_frame)
        self.main_tab = ttk.Frame(self.notebook)
        self.admin_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main")
        self.notebook.add(self.admin_tab, text="Vault")
        self.notebook.pack(fill="both", expand=True)
        
        self.current_input_data = None
        self.current_result_data = None