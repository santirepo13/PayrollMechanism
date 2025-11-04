"""
Main GUI window for BroadSpec Payment Calculator.
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

from broadspec.utils.pdf_preview import PDFPreviewer

# Import refactored components
from broadspec.ui.components.window_setup import WindowSetup
from broadspec.ui.components.main_tab_ui import MainTabUI
from broadspec.ui.components.admin_tab_ui import AdminTabUI
from broadspec.ui.components.calculation_handler import CalculationHandler
from broadspec.ui.components.pdf_saver import PDFSaver
from broadspec.ui.components.model_image_saver import ModelImageSaver
from broadspec.ui.components.resolution_manager import ResolutionManager
from broadspec.ui.components.pdf_preview_handler import PDFPreviewHandler


class BroadSpecGUI:
    """Main GUI application class implementing View in MVC pattern."""
    
    def __init__(self, root: tk.Tk, config: Dict[str, Any], controller):
        """Initialize GUI."""
        self.root = root
        self.config = config
        self.controller = controller
        
        # Initialize window setup first
        self.window_setup = WindowSetup(root, config)
        
        # Initialize UI components
        self.main_tab_ui = MainTabUI(self.window_setup.main_tab, self.window_setup)
        self.admin_tab_ui = AdminTabUI(self.window_setup.admin_tab, self.window_setup, controller)
        
        # Initialize functionality components
        self.calculation_handler = CalculationHandler(self.main_tab_ui, self.window_setup, controller)
        self.pdf_saver = PDFSaver(self.main_tab_ui, self.window_setup, controller)
        self.model_image_saver = ModelImageSaver(self.main_tab_ui, self.window_setup, controller)
        self.resolution_manager = ResolutionManager(self.window_setup, self.admin_tab_ui)
        self.pdf_preview_handler = PDFPreviewHandler(self.window_setup, self.admin_tab_ui, controller)
    
    # Direct access to component methods - no delegation needed
    # Components are directly accessible through their instances
    
    @property
    def main_tab(self):
        """Access to main tab UI component."""
        return self.main_tab_ui
    
    @property
    def admin_tab(self):
        """Access to admin tab UI component."""
        return self.admin_tab_ui
    
    @property
    def notebook(self):
        """Access to notebook widget."""
        return self.window_setup.notebook