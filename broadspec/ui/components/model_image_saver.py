"""
Model image saving component for BroadSpec Payment Calculator.
"""
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import tkinter.font as tkfont

from broadspec.utils.pdf_protocols import generate_filename


class ModelImageSaver:
    """Handles saving model screenshots as images."""
    
    def __init__(self, main_tab_ui, window_setup, controller):
        """Initialize model image saver."""
        self.main_tab_ui = main_tab_ui
        self.window_setup = window_setup
        self.controller = controller
        
        # Set the save model image button command directly
        self.main_tab_ui.save_model_image_btn.config(command=self.save_model_image)
    
    def save_model_image(self):
        """
        Save a cropped image (JPG/PNG) of the model screenshot area.

        Behavior:
        - Takes the text in the 'model_text' widget.
        - Finds the last separator line composed of dashes (-----) and crops the content
          to a small amount taller than that final separator (keeps one extra line).
        - Renders the cropped text to an image using a monospace font and asks the user
          where to save the file (defaults to .jpg).
        """
        if not self.window_setup.current_input_data or not self.window_setup.current_result_data:
            messagebox.showwarning("No Data", "Please calculate first before saving")
            return

        try:
            # Get full content from model text widget
            content = self.main_tab_ui.model_text.get("1.0", tk.END)
            lines = content.splitlines()

            # Find the last line that looks like a separator (only dashes, length >= 3)
            sep_idx = None
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if len(line) >= 3 and set(line) == {"-"}:
                    sep_idx = i
                    break

            # Include a little space below the separator (one extra line)
            if sep_idx is not None:
                end_idx = min(len(lines), sep_idx + 2)
            else:
                end_idx = len(lines)

            selected_lines = lines[:end_idx]

            # Trim trailing blank lines for a tighter image
            while selected_lines and selected_lines[-1].strip() == "":
                selected_lines.pop()

            text_to_render = "\n".join(selected_lines) or " "

            # Choose a monospace font, fall back to default if not available
            font_size = 14
            try:
                # Try common monospace fonts
                font = ImageFont.truetype("Courier New.ttf", font_size)
            except Exception:
                try:
                    font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
                except Exception:
                    font = ImageFont.load_default()

            # Render text to an image to match the on-screen Text widget as closely as possible.
            padding = 12

            # Create a tiny dummy draw for fallback measuring
            dummy_img = Image.new("RGB", (1, 1), "white")
            draw_dummy = ImageDraw.Draw(dummy_img)

            # Helper measurement function (uses Pillow methods when possible)
            def _measure_text(draw_obj, text, font_obj):
                try:
                    bbox = draw_obj.textbbox((0, 0), text, font=font_obj)
                    return bbox[2] - bbox[0], bbox[3] - bbox[1]
                except Exception:
                    pass
                try:
                    return font_obj.getsize(text)
                except Exception:
                    pass
                try:
                    return draw_obj.textsize(text, font=font_obj)
                except Exception:
                    avg_char_w = font_size * 0.6
                    return int(len(text) * avg_char_w), font_size + 4

            lines_to_measure = text_to_render.split("\n")

            # Try to mirror the widget's font and metrics
            try:
                tkf = tkfont.Font(font=self.main_tab_ui.model_text.cget("font"))
                fam = tkf.cget("family")
                tk_size = int(abs(int(tkf.cget("size")))) if tkf.cget("size") else font_size
                try:
                    line_h = tkf.metrics("linespace")
                except Exception:
                    line_h = tk_size + 4
            except Exception:
                fam = None
                tk_size = font_size
                line_h = font_size + 4

            # Try loading a matching TTF for the widget font family
            font_pil = None
            candidates = []
            if fam:
                fam_lower = fam.lower()
                if "courier" in fam_lower or "mono" in fam_lower:
                    candidates = ["Courier New.ttf", "DejaVuSansMono.ttf", "LiberationMono-Regular.ttf"]
                else:
                    candidates = [f"{fam}.ttf", "DejaVuSansMono.ttf", "Courier New.ttf"]
            else:
                candidates = ["DejaVuSansMono.ttf", "Courier New.ttf"]

            for cand in candidates:
                try:
                    font_pil = ImageFont.truetype(cand, tk_size)
                    break
                except Exception:
                    font_pil = None

            # Fall back to previously-resolved PIL font object if no TTF found
            if font_pil is None:
                font_pil = font

            # Determine image width: prefer widget pixel width so layout matches what's on screen
            widget_w = self.main_tab_ui.model_text.winfo_width()
            if widget_w and widget_w > 10:
                img_w = max(100, widget_w)
            else:
                # Fallback: measure longest line width
                max_w = 0
                for ln in lines_to_measure:
                    try:
                        # textlength is available in newer Pillow; fall back to measure helper
                        if hasattr(draw_dummy, "textlength"):
                            w = draw_dummy.textlength(ln, font=font_pil)
                        else:
                            w = _measure_text(draw_dummy, ln, font_pil)[0]
                    except Exception:
                        w = _measure_text(draw_dummy, ln, font_pil)[0]
                    if w > max_w:
                        max_w = w
                img_w = int(max_w + padding * 2)

            # Height: use widget line spacing if available for closer visual match
            # Calculate height from number of lines and line_h, with padding
            img_h = int(line_h * len(lines_to_measure) + padding * 2)

            # Create final image with the same background color as the Text widget.
            # Tk may return platform/system color names (e.g. 'SystemWindow') which PIL
            # does not understand. Convert to an RGB hex using winfo_rgb when possible.
            try:
                bg = self.main_tab_ui.model_text.cget("background") or "white"
                try:
                    r, g, b = self.main_tab_ui.model_text.winfo_rgb(bg)
                    # winfo_rgb returns 0-65535 per channel; convert to 0-255
                    hex_bg = '#{0:02x}{1:02x}{2:02x}'.format(r // 256, g // 256, b // 256)
                except Exception:
                    # If conversion fails, fall back to the raw value or white
                    hex_bg = bg if isinstance(bg, str) else "white"
            except Exception:
                hex_bg = "white"

            img = Image.new("RGB", (max(1, int(img_w)), max(1, int(img_h))), hex_bg)
            draw = ImageDraw.Draw(img)

            # Left padding matches typical text widget inset
            left_pad = padding
            y = padding
            for ln in lines_to_measure:
                draw.text((left_pad, y), ln, fill="black", font=font_pil)
                # Advance by widget line height when possible for consistent spacing
                y += line_h

            # Auto-save image into ./img using the same filename protocol as PDFs (no dialog)
            try:
                img_dir = os.path.join(os.getcwd(), "img")
                os.makedirs(img_dir, exist_ok=True)

                # Try to build the exact PDF filename used by the app, then replace .pdf -> .jpg
                try:
                    result_obj = None
                    if hasattr(self.controller, '_dict_to_calculation_result'):
                        # controller helper converts dict -> CalculationResult for generate_filename
                        result_obj = self.controller._dict_to_calculation_result(self.window_setup.current_result_data)
                    pdf_name = generate_filename(self.window_setup.current_input_data, result_obj)
                except Exception:
                    # Fallback simple name if generate_filename isn't available for some reason
                    model_id = (self.window_setup.current_input_data.get('model_id') or "").strip()
                    model_name = (self.window_setup.current_input_data.get('model_name') or "").strip()
                    date_str = (self.window_setup.current_result_data.get('date') or datetime.now().strftime("%Y-%m-%d"))
                    pdf_name = f"{model_id} - {model_name} - {date_str}.pdf"

                base = os.path.splitext(pdf_name)[0]
                filename = f"{base}.jpg"
                filename = os.path.basename(filename)  # ensure no directories
                filepath = os.path.join(img_dir, filename)

                # Save as high-quality JPEG
                rgb = img.convert("RGB")
                rgb.save(filepath, format="JPEG", quality=90)

                messagebox.showinfo("Saved Image", f"Model image automatically saved: {filepath}")
            except Exception as _save_err:
                # If automatic save fails, fall back to asking the user
                try:
                    filepath = filedialog.asksaveasfilename(
                        defaultextension=".jpg",
                        filetypes=[("JPEG image", "*.jpg"), ("PNG image", "*.png"), ("All files", "*.*")],
                        title="Save Model Image"
                    )
                    if not filepath:
                        return
                    _, ext = os.path.splitext(filepath)
                    ext = ext.lower()
                    if ext == ".png":
                        img.save(filepath, format="PNG")
                    else:
                        rgb = img.convert("RGB")
                        rgb.save(filepath, format="JPEG", quality=90)
                    messagebox.showinfo("Saved Image", f"Model image saved: {filepath}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save model image: {str(e)}")

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save model image: {str(e)}")