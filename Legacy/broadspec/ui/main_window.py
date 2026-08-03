import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

from broadspec.utils.pdf_preview import PDFPreviewer

from broadspec.ui.components.window_setup import WindowSetup
from broadspec.ui.components.main_tab_ui import MainTabUI
from broadspec.ui.components.vault_tab_ui import VaultTabUI
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
        
        self.window_setup = WindowSetup(root, config)

        # Track temp files created during runtime so we can delete them on exit.
        # Components that create temp files should add paths to this set:
        #   self.window_setup.temp_files.add(temp_path)
        if not hasattr(self.window_setup, "temp_files"):
            self.window_setup.temp_files = set()
        
        # Register handler to clean up temp files when window closes (user clicks X)
        try:
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            # If protocol registration fails, continue without crash
            pass
        
        self.main_tab_ui = MainTabUI(self.window_setup.main_tab, self.window_setup)
        self.vault_tab_ui = VaultTabUI(self.window_setup.vault_tab, self.window_setup, controller)
        self.admin_tab_ui = AdminTabUI(self.window_setup.admin_tab, self.window_setup)

        self.calculation_handler = CalculationHandler(self.main_tab_ui, self.window_setup, controller)
        self.pdf_saver = PDFSaver(self.main_tab_ui, self.window_setup, controller)
        self.model_image_saver = ModelImageSaver(self.main_tab_ui, self.window_setup, controller)
        self.resolution_manager = ResolutionManager(self.window_setup, self.vault_tab_ui)
        self.pdf_preview_handler = PDFPreviewHandler(self.window_setup, self.vault_tab_ui, controller)
    
    def _on_close(self):
        """Cleanup temp files and exit the application."""
        try:
            # Inform the user
            try:
                messagebox.showinfo("Exiting", "Deleting temporary files and exiting...")
            except Exception:
                pass

            # Delete registered temp files
            temp_files = getattr(self.window_setup, "temp_files", None)
            if temp_files:
                for p in list(temp_files):
                    try:
                        if p and os.path.exists(p):
                            os.remove(p)
                    except Exception:
                        # best-effort deletion; ignore failures
                        pass
                try:
                    temp_files.clear()
                except Exception:
                    pass
        finally:
            # Destroy root window and exit
            try:
                self.root.destroy()
            except Exception:
                pass

    @property
    def admin_tab(self):
        """Access to admin tab UI component."""
        return self.admin_tab_ui

    @property
    def main_tab(self):
        """Access to main tab UI component."""
        return self.main_tab_ui

    @property
    def vault_tab(self):
        """Access to vault tab UI component"""
        return self.vault_tab_ui
    
    @property
    def notebook(self):
        """Access to notebook widget"""
        return self.window_setup.notebook