"""
PDF preview utilities for BroadSpec Payment Calculator.
"""
import os
import tempfile
import fitz  # PyMuPDF
from typing import Optional, Tuple
from PIL import Image, ImageTk
import tkinter as tk


class PDFPreviewer:
    """Handles PDF preview functionality."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.preview_enabled = self.config.get('ui', {}).get('pdf_preview_enabled', True)
        self.current_pdf_path = None
        self.current_doc = None
        self.current_page = 0
        self.zoom_level = 1.0
        
    def is_enabled(self) -> bool:
        return self.preview_enabled
    
    def open_pdf(self, pdf_path: str) -> bool:
        """
        Open a PDF file for preview.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.preview_enabled:
            return False
            
        try:
            if not os.path.exists(pdf_path):
                return False
                
            self.current_pdf_path = pdf_path
            self.current_doc = fitz.open(pdf_path)
            self.current_page = 0
            return True
            
        except Exception:
            return False
    
    def get_page_count(self) -> int:
        """Get the number of pages in the current PDF."""
        if not self.current_doc:
            return 0
        return len(self.current_doc)
    
    def get_current_page(self) -> int:
        """Get the current page number (0-indexed)."""
        return self.current_page
    
    def set_current_page(self, page_num: int) -> bool:
        """
        Set the current page number.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.current_doc or page_num < 0 or page_num >= len(self.current_doc):
            return False
            
        self.current_page = page_num
        return True
    
    def get_page_image(self, page_num: int = None, zoom: float = None) -> Optional[Image.Image]:
        """
        Get a PIL Image for the specified page.
        
        Args:
            page_num: Page number (0-indexed), defaults to current page
            zoom: Zoom level, defaults to current zoom level
            
        Returns:
            PIL Image if successful, None otherwise
        """
        if not self.current_doc:
            return None
            
        if page_num is None:
            page_num = self.current_page
            
        if zoom is None:
            zoom = self.zoom_level
            
        if page_num < 0 or page_num >= len(self.current_doc):
            return None
            
        try:
            page = self.current_doc[page_num]
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            return img
            
        except Exception:
            return None
    
    def get_page_tk_image(self, page_num: int = None, zoom: float = None) -> Optional[ImageTk.PhotoImage]:
        """
        Get a Tkinter-compatible PhotoImage for the specified page.
        
        Args:
            page_num: Page number (0-indexed), defaults to current page
            zoom: Zoom level, defaults to current zoom level
            
        Returns:
            Tkinter PhotoImage if successful, None otherwise
        """
        img = self.get_page_image(page_num, zoom)
        if img is None:
            return None
            
        try:
            return ImageTk.PhotoImage(img)
        except Exception:
            return None
    
    def set_zoom(self, zoom: float) -> bool:
        """
        Set the zoom level.
        
        Args:
            zoom: Zoom level (1.0 = 100%)
            
        Returns:
            True if successful, False otherwise
        """
        if zoom <= 0:
            return False
            
        self.zoom_level = zoom
        return True
    
    def get_zoom(self) -> float:
        """Get the current zoom level."""
        return self.zoom_level
    
    def close(self):
        """Close the current PDF document."""
        if self.current_doc:
            self.current_doc.close()
            self.current_doc = None
            self.current_pdf_path = None
            self.current_page = 0