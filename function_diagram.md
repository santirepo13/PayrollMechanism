# BroadSpec Payment Calculator - Function Diagram

## Project Overview
This is a Python Tkinter application for calculating payments with secure document storage capabilities.

## Core Components

### 1. Entry Points
- [`script.py`](script.py:1) - Simple launcher that initializes the GUI
- [`broadspec_gui.py`](broadspec_gui.py:1) - Main application file containing all functionality

### 2. Main Class: BroadSpecCalculator
Located in [`broadspec_gui.py`](broadspec_gui.py:222-1663)

#### 2.1 UI Layout Functions
- [`compute_inner_box_dimensions()`](broadspec_gui.py:15-39) - Calculates responsive UI dimensions
- [`estimate_text_dimensions_from_pixels()`](broadspec_gui.py:42-51) - Estimates text widget sizes
- [`adjust_common_widgets_to_inner()`](broadspec_gui.py:54-111) - Adjusts widget sizes based on window

#### 2.2 Form Management
- [`__init__()`](broadspec_gui.py:223-470) - Initializes the entire GUI
- [`on_percentage_change()`](broadspec_gui.py:472-489) - Handles percentage selection changes
- [`clear_fields()`](broadspec_gui.py:556-588) - Resets all form fields

#### 2.3 Dynamic Form Elements
- [`add_advance_field()`](broadspec_gui.py:491-508) - Adds advance payment entry
- [`remove_advance_field()`](broadspec_gui.py:510-520) - Removes advance payment entry
- [`add_other_site_field()`](broadspec_gui.py:522-542) - Adds other site payment entry
- [`remove_other_site_field()`](broadspec_gui.py:544-554) - Removes other site payment entry

#### 2.4 Core Business Logic
- [`calculate()`](broadspec_gui.py:590-812) - Main payment calculation logic
- [`save_pdf()`](broadspec_gui.py:814-889) - Generates and saves PDF receipts

#### 2.5 Secure Vault System
- [`ensure_secure_store()`](broadspec_gui.py:892-931) - Initializes encrypted storage
- [`prune_perfile_encrypted()`](broadspec_gui.py:933-958) - Removes legacy encrypted files
- [`load_vault_index()`](broadspec_gui.py:960-983) - Loads vault metadata
- [`save_vault_index()`](broadspec_gui.py:985-995) - Saves vault metadata
- [`build_vault_index_from_vault()`](broadspec_gui.py:997-1032) - Rebuilds index from vault
- [`add_to_single_vault()`](broadspec_gui.py:1034-1101) - Adds PDF to encrypted vault

#### 2.6 Admin UI Functions
- [`init_secure_ui()`](broadspec_gui.py:1103-1218) - Creates admin interface
- [`refresh_from_disk()`](broadspec_gui.py:1220-1229) - Reloads vault from disk
- [`refresh_secure_listbox()`](broadspec_gui.py:1231-1250) - Updates file list
- [`on_secure_select()`](broadspec_gui.py:1252-1379) - Handles file selection
- [`_set_preview_text()`](broadspec_gui.py:1381-1385) - Updates preview text
- [`_clear_preview()`](broadspec_gui.py:1387-1403) - Clears preview area
- [`_on_preview_mousewheel()`](broadspec_gui.py:1405-1411) - Handles preview scrolling
- [`open_preview_file()`](broadspec_gui.py:1413-1433) - Opens PDF in system viewer

#### 2.7 Vault Operations
- [`import_pdfs_into_vault()`](broadspec_gui.py:1435-1461) - Imports external PDFs
- [`export_selected_secure_pdf()`](broadspec_gui.py:1463-1517) - Exports selected PDFs
- [`delete_selected_secure_pdf()`](broadspec_gui.py:1519-1568) - Deletes selected PDFs
- [`update_vault_stats()`](broadspec_gui.py:1570-1585) - Updates vault statistics

#### 2.8 View Management
- [`toggle_view()`](broadspec_gui.py:1587-1604) - Switches between display modes
- [`apply_1366_view()`](broadspec_gui.py:1606-1621) - Applies 1366x768 layout
- [`apply_1080_view()`](broadspec_gui.py:1623-1639) - Applies 1920x1080 layout
- [`update_layout_button_text()`](broadspec_gui.py:1641-1649) - Updates button text
- [`on_root_configure()`](broadspec_gui.py:1651-1663) - Handles window resize

### 3. Utility Functions
- [`sanitize_filename()`](broadspec_gui.py:154-162) - Cleans filenames for storage
- [`human_readable_size()`](broadspec_gui.py:164-173) - Formats file sizes
- [`parse_filename_metadata()`](broadspec_gui.py:175-220) - Extracts metadata from filenames

## Data Flow
1. User inputs payment data in the Main tab
2. [`calculate()`](broadspec_gui.py:590-812) processes the data and generates receipts
3. [`save_pdf()`](broadspec_gui.py:814-889) creates PDF and stores in encrypted vault
4. Admin tab provides vault management through secure UI functions

## Dependencies
- tkinter - GUI framework
- reportlab - PDF generation
- cryptography - Encryption (optional)
- PyMuPDF - PDF rendering (optional)
- Pillow - Image processing (optional)