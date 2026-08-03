# BroadSpec Payment Calculator — SRS

> Generated from `srstemplateV1.1.md` with current project state.
> Not applicable sections are left empty but headers are retained for reference.

```text
SRS_REVIEW_CONTEXT
```

---

# 1. Purpose

## 1.1 System Purpose

```text
The system exists to:
Calculate COP/USD payment amounts for models based on token production (TKS),
TRM exchange rates, percentage tiers, bonus thresholds, fines, advances, and
other-site earnings. It generates PDF receipts stored in an encrypted local vault
and provides an admin COP-to-USD conversion calculator.
```

## 1.2 Review Purpose

```text
This SRS context is intended to help an LLM review:
- Bugs
- Missing requirements
- Compliance failures
- Test coverage gaps
- Implementation mismatches
- Security violations
- Data handling errors
```

---

# 2. Scope

## 2.1 In Scope

| ID     | In-Scope Item |
| ------ | ------------- |
| SC-001 | Payment calculation from tokens, TRM, percentage |
| SC-002 | Bonus tier calculation (10k–20k+ TKS, 3%–10%) |
| SC-003 | Fine calculation (studio only, ≤60%) |
| SC-004 | Advance and extra payment deductions/additions |
| SC-005 | Other-site earnings (USD or TKS) aggregation |
| SC-006 | PDF receipt generation (ReportLab, 2-page format) |
| SC-007 | Encrypted vault storage (Fernet + ZIP) |
| SC-008 | Vault management (import, export, delete, preview) |
| SC-009 | PDF preview with zoom and pagination (PyMuPDF) |
| SC-010 | Model receipt screenshot export (Pillow, JPEG/PNG) |
| SC-011 | Admin COP-to-USD reverse calculator |
| SC-012 | UI resolution toggle (1920x1080 / 1366x768) |
| SC-013 | Input validation for all form fields |
| SC-014 | Modular architecture (MVC pattern) |

## 2.2 Out of Scope

| ID      | Out-of-Scope Item | Reason |
| ------- | ----------------- | ------ |
| OOS-001 | Multi-user support | Single-user desktop application |
| OOS-002 | Web or mobile interface | Desktop-only (Tkinter) |
| OOS-003 | External API exposure | No network services |
| OOS-004 | Database persistence | File-based vault only |
| OOS-005 | LLM integration | No AI/LLM component |
| OOS-006 | Cloud synchronization | Fully local application |
| OOS-007 | Internationalization (i18n) | Single-language (English/Spanish hybrid) |

---

# 3. Glossary, Definitions, Acronyms, and Domain Terms

This section is mandatory for LLM review.

| Term | Type           | Definition | System Meaning |
| ---- | -------------- | ---------- | -------------- |
| TRM | Acronym | Tasa Representativa del Mercado (Colombian official exchange rate) | `trm_official_cop` — float, manual entry, base exchange rate |
| BTK TRM | Acronym | BroadSpec Token exchange rate (alternative TRM) | `btk_trm_cop` — float, manual entry, used for transfer cost calculation |
| TKS | Acronym | Tokens (BroadSpec currency unit) | Integer input; 20 TKS = 1 USD (`token_to_usd_rate`) |
| COP | Acronym | Colombian Peso | Output currency; all final payment amounts in COP |
| USD | Acronym | United States Dollar | Intermediate currency for token conversion and platform transfer |
| Vault | Domain term | Encrypted ZIP archive storing all receipt PDFs | `single_vault.zip.enc` — Fernet-encrypted ZIP file in `.secure_store/` |
| Fernet | Technical term | Symmetric encryption from `cryptography` library | Used to encrypt/decrypt vault and index files |
| Model | Role | Content creator earning tokens | Has model_id, model_name, and earns tokens based on percentage |
| Studio Worker | Role | Model working from studio (≤60% cut) | Subject to fines |
| Home Worker | Role | Model working from home (>60% cut) | Not subject to fines |
| Percentage | Domain term | Share of token value the model receives | 60%, 70%, or 75% — determines fine applicability |
| Advance | Domain term | Pre-payment deducted from final total | Dated amount in COP |
| Extra | Domain term | Additional payment added to final total | Dated amount in COP |
| Fine | Domain term | Penalty deduction (30,000 COP each) | Only applied at ≤60% (studio); customizable amount |
| Other Site | Domain term | Earnings from external platforms | Amounts in USD or TKS, converted and summed for bonus |
| Bonus | Domain term | Extra percentage added for high token production | 5 tiers: 10k→3%, 12.5k→4.5%, 15k→6%, 17.5k→8%, 20k→10% |
| `token_to_usd_rate` | Technical term | Conversion factor: 20 TKS per 1 USD | Defined in `config.yaml:31` |
| `trm_adjustment` | Technical term | COP deduction from official TRM | Default -300 COP; -200 COP if tokens ≥ 3,000 (unless overridden) |
| `transfer_cost` | Technical term | Flat transfer fee in USD | $6.99 USD base + 19% tax (`transfer_cost_tax`) |
| `token_value_cop` | Technical term | BTK TRM × 0.05 | Used to compute `usd_to_send_platform` |
| `usd_to_send_platform` | Technical term | USD amount to transfer to platform | `(total_cop + transfer_cost_cop) / token_value_cop / token_to_usd_rate` |
| Receipt | Domain term | Two-page PDF document (full receipt + simplified model receipt) | Generated by ReportLab, stored in vault |

---

# 4. Requirement Language Rules

Include this because the LLM needs to understand requirement force.

| Word     | Meaning                              |
| -------- | ------------------------------------ |
| Shall    | Mandatory                            |
| Must     | Mandatory                            |
| Must not | Forbidden                            |
| Should   | Recommended but not mandatory        |
| May      | Optional / allowed                   |
| Can      | Capability, not necessarily required |

---

# 5. System Context

## 5.1 Product Overview

| Area                       | Description                                                                  |
| -------------------------- | ---------------------------------------------------------------------------- |
| Product name               | BroadSpec Payment Calculator                                                 |
| Product type               | Desktop app (Python Tkinter)                                                 |
| Primary users              | Payment operator / administrator                                            |
| Main goal                  | Calculate model payments, generate encrypted PDF receipts, manage vault     |
| Deployment environment     | Windows (primary), cross-platform Python 3.8+                               |
| Main external dependencies | ReportLab (PDF), cryptography (encryption), PyMuPDF (preview), Pillow (images) |

## 5.2 Actors and External Systems

| Actor / System | Type            | Interaction With System |
| -------------- | --------------- | ----------------------- |
| Operator       | Human user      | Enters payment data, runs calculations, saves PDFs, manages vault |
| File system    | Local storage   | Reads/writes config, vault files, receipts, images |
| cryptography   | Library         | Fernet symmetric encryption/decryption of vault and index |
| ReportLab      | Library         | Generates PDF receipts (canvas-based drawing) |
| PyMuPDF (fitz) | Library         | Renders PDF pages for preview, extracts page images |
| Pillow (PIL)   | Library         | Creates JPEG/PNG screenshots of model receipts |
| PyYAML         | Library         | Parses `config.yaml` configuration file |

---

# 6. User Classes and Permissions

| User Class      | Description | Allowed Actions | Forbidden Actions |
| --------------- | ----------- | --------------- | ----------------- |
| Operator        | Single user operating the application | Enter payment data, calculate, save PDFs, manage vault, export/import/delete vault entries, use admin COP-USD calculator, toggle resolution, preview PDFs | None |

---

# 7. Functional Requirements

## 7.1 Functional Requirement Format

| Field                  | Value               |
| ---------------------- | ------------------- |
| Requirement ID         | FR-001              |
| Requirement            | The system shall... |
| Actor                  |                     |
| Trigger                |                     |
| Input                  |                     |
| Processing Rule        |                     |
| Output                 |                     |
| Error Behavior         |                     |
| Acceptance Criteria    |                     |
| Related Business Rules |                     |
| Related Test Cases     |                     |

## 7.2 Functional Requirements

| ID     | Requirement      | Acceptance Criteria |
| ------ | ---------------- | ------------------- |
| FR-001 | The system shall calculate payment amounts from model input data (tokens, TRM, percentage, other sites, advances, fines, extras, previous fortnight USD) | `test_calculate_basic_payment` passes; total_cop > 0 and total_usd > 0 |
| FR-002 | The system shall apply bonus percentage based on total tokens across all sites (5 tiers: 10k→3%, 12.5k→4.5%, 15k→6%, 17.5k→8%, 20k→10%) | `test_calculate_bonus_percentage_new_structure` passes for all 5 tier boundaries |
| FR-003 | The system shall aggregate tokens from other sites (USD→TKS conversion, TKS direct) for bonus calculation | `test_calculate_bonus_with_other_sites_usd`, `test_calculate_bonus_with_other_sites_tks`, `test_calculate_bonus_with_mixed_sites` pass |
| FR-004 | The system shall allow bonus to be disabled via `disable_bonus` flag | `test_calculate_bonus_disable_bonus_flag` passes |
| FR-005 | The system shall apply fines only when percentage ≤ 60% (studio workers); 30,000 COP per fine or custom amount | `test_calculate_with_fines_studio`, `test_calculate_with_fines_home_worker`, `test_calculate_with_custom_fine` pass |
| FR-006 | The system shall apply a TRM adjustment of -300 COP by default, reduced to -200 COP when total tokens ≥ 3,000, unless overridden | Default trm_broadspec_cop = trm_official_cop - 300 (or -200); `override_high_tokens_trm` flag preserves -300 |
| FR-007 | The system shall deduct advances from and add extras to the final payment total | `test_calculate_with_advances` passes; extras_total and advances_total reflected in total_cop |
| FR-008 | The system shall calculate transfer cost as `(6.99 + 6.99 × 0.19) × BTK TRM` | transfer_cost_cop = 6.99 × 1.19 × btk_trm_cop |
| FR-009 | The system shall calculate platform USD as `(total_cop + transfer_cost_cop) / (BTK_TRM × 0.05) / 20` | `usd_to_send_platform` included in result and receipts |
| FR-010 | The system shall generate two-page PDF receipts (full receipt + model/payment confirmation) using ReportLab | `test_generate_pdf_success` passes; output file >0 bytes with correct filename format |
| FR-011 | The system shall store receipt PDFs in an encrypted ZIP vault (Fernet encryption) without creating local file copies | `test_add_file`, `test_retrieve_file` pass; `save_receipt()` writes to vault via `add_bytes()` |
| FR-012 | The system shall maintain an encrypted vault index (`vault_index.json.enc`) mapping vault entries to metadata | `test_load_index_with_data`, `test_save_index` pass |
| FR-013 | The system shall allow export of PDFs from vault to local file system | `export_from_vault()` retrieves file bytes and writes to disk |
| FR-014 | The system shall allow deletion of PDFs from vault (individual or batch) | `test_delete_files`, `test_delete_files_multiple` pass |
| FR-015 | The system shall allow import of external PDFs into the vault | `import_to_vault()` adds external files; `test_add_file` pass |
| FR-016 | The system shall provide PDF preview with zoom (50%–200%) and page navigation | `open_pdf()`, `get_page_tk_image()`, `set_zoom()`, `set_current_page()` in `PDFPreviewer` |
| FR-017 | The system shall allow saving a cropped screenshot of the model receipt as JPEG/PNG | `save_model_image()` renders Text widget content to Pillow image, saves as JPEG |
| FR-018 | The system shall provide an admin COP-to-USD reverse calculator (compute required gross USD for target COP) | `AdminTabUI._calculate_usd_amount()` solves for gross USD with retention tax and transfer fee |
| FR-019 | The system shall support two UI resolutions: 1920×1080 and 1366×768 | `ResolutionManager.toggle_resolution()` scales fonts, widgets, and layout |
| FR-020 | The system shall validate all form inputs before calculation (required fields, numeric ranges, negative values) | `test_validate_data_valid`, `test_validate_data_missing_model_id`, `test_validate_data_negative_values` pass |
| FR-021 | The system shall generate filenames following the convention: `{model_id} - {model_name} - {tokens_total} TKS - {usd} USD - {cop} COP - {date}.pdf` | `test_generate_filename_with_result` passes; USD uses 3 decimal digits, COP uses dot-separated thousands |
| FR-022 | The system shall support bonus token ranges (user specifies which tokens qualify for bonus) | `bonus_tokens` field on `PaymentData`; ratio-based weighted percentage calculation |

---

# 8. Use Cases / User Flows

## UC-001: Calculate Payment

| Field                | Description |
| -------------------- | ----------- |
| Use Case ID          | UC-001      |
| Actor                | Operator    |
| Goal                 | Compute model payment amount in COP and USD |
| Preconditions        | config.yaml loaded, calculators initialized |
| Trigger              | User clicks "Calculate" button |
| Postconditions       | Full receipt and payment confirmation displayed in UI |
| Related Requirements | FR-001 through FR-009, FR-020 |

## Main Flow

| Step | Actor Action | System Response |
| ---- | ------------ | --------------- |
| 1    | Enter model ID, model name, TRM Official, BTK TRM | Fields accept values |
| 2    | Select percentage (60%/70%/75%) | System enables/disables fines section based on selection |
| 3    | Enter tokens (TKS) | |
| 4    | Add other sites (USD or TKS) with amounts | |
| 5    | Enter previous fortnight USD | |
| 6    | Add advances with dates and COP amounts | |
| 7    | Add extras with dates and COP amounts | |
| 8    | Enter fines count or custom fine amount | |
| 9    | Optionally check "Disable All Bonuses" or "Always apply -300 TRM" | |
| 10   | Click "Calculate" | System collects form data, validates, computes payment via `PaymentCalculator.calculate()`, displays full receipt and payment confirmation in Text widgets |

## Alternative Flows

| Flow ID | Condition | Expected Behavior |
| ------- | --------- | ----------------- |
| AF-001  | Percentage > 60% selected | Fines fields disabled, label shows "Fines (Disabled - Home Worker)" |
| AF-002  | Custom fine amount entered (>0) | Fines count ignored; custom amount used |
| AF-003  | `disable_bonus` checked | Bonus percentage forced to 0% regardless of token count |
| AF-004  | `override_high_tokens_trm` checked | TRM adjustment stays at -300 regardless of token count |
| AF-005  | Other sites include TKS type | Amount passed directly as TKS (not converted to USD 1/20th) for token total |

## Exception Flows

| Exception ID | Error Condition | Expected System Response |
| ------------ | --------------- | ------------------------ |
| EX-001       | Model ID blank | Validation error: "Model ID is required" |
| EX-002       | TRM Official ≤ 0 | Validation error: "TRM Official COP must be greater than 0" |
| EX-003       | BTK TRM ≤ 0 | Validation error: "BTK TRM COP must be greater than 0" |
| EX-004       | Negative values in tokens, advances, fines | Validation errors for each negative field |
| EX-005       | Invalid numeric input | Messagebox showing calculation error |

---

# 9. User Stories

## 9.1 User Story Format

| Field | Value |
| ----- | ----- |
| User Story ID | US-001 |
| User Role | |
| Story | As a [user role], I want [goal], so that [reason]. |
| Priority | High / Medium / Low |
| Related Use Case | |
| Related Functional Requirements | |
| Related UI Requirements | |
| Related API Requirements | |
| Acceptance Criteria | |
| Related Test Cases | |

## 9.2 User Stories

| ID | User Role | User Story | Priority | Related Requirements | Related Test Cases |
| -- | --------- | ---------- | -------- | -------------------- | ------------------ |
| US-001 | Operator | As a payment operator, I want to calculate model payments from tokens and TRM so that I can determine the correct amount to pay. | High | FR-001, FR-005, FR-006, FR-007, FR-008, FR-020 | test_calculate_basic_payment, test_calculate_with_fines_studio |
| US-002 | Operator | As a payment operator, I want bonus percentages automatically applied based on total token production across all sites so that high-performing models are rewarded. | High | FR-002, FR-003, FR-004 | test_calculate_bonus_percentage_new_structure, test_calculate_bonus_with_other_sites_usd |
| US-003 | Operator | As a payment operator, I want receipt PDFs stored securely in an encrypted vault so that sensitive payment data is protected. | High | FR-010, FR-011, FR-012 | test_add_file, test_save_index |
| US-004 | Operator | As a payment operator, I want to manage vault contents (view, export, delete, import PDFs) so that I can maintain payment records. | Medium | FR-013, FR-014, FR-015 | test_retrieve_file, test_delete_files |
| US-005 | Operator | As a payment operator, I want to preview PDF receipts directly in the application so that I can verify payment details without opening external programs. | Medium | FR-016 | PDFPreviewer.open_pdf, update_pdf_display |
| US-006 | Operator | As a payment operator, I want to save a screenshot of the model's payment confirmation so that I can share it quickly. | Medium | FR-017 | ModelImageSaver.save_model_image |
| US-007 | Operator | As a payment operator, I want to calculate the required gross USD amount for a target COP amount so that I can plan transfers. | Medium | FR-018 | AdminTabUI._calculate_usd_amount |
| US-008 | Operator | As a payment operator, I want to restrict which tokens qualify for bonus via a manual range input so that bonuses reflect only recent production. | Low | FR-022 | bonus_tokens field in PaymentData |

---

# 10. Business Rules

| Rule ID | Business Rule | Related Requirements |
| ------- | ------------- | -------------------- |
| BR-001  | Total tokens across all sites = main tokens + other-site TKS + (other-site USD × 20) | FR-002, FR-003 |
| BR-002  | Bonus tiers: <10k→0%, ≥10k→3%, ≥12.5k→4.5%, ≥15k→6%, ≥17.5k→8%, ≥20k→10% | FR-002 |
| BR-003  | TRM BroadSpec = TRM Official − 300 COP (or −200 if total tokens ≥ 3,000) | FR-006 |
| BR-004  | Fines apply only when percentage ≤ 60% (studio worker); disabled for >60% (home worker) | FR-005 |
| BR-005  | Transfer cost = 6.99 USD base + 19% tax, converted at BTK TRM | FR-008 |
| BR-006  | Percentage values: 60%, 70%, 75% (selectable from dropdown) | FR-001 |
| BR-007  | Token to USD rate: 20 TKS = 1 USD | FR-003, FR-009 |
| BR-008  | Final payment = BroadSpec Value − Advances − Fines + Extras | FR-007 |
| BR-009  | Net USD from tokens = (tokens / 20) × final_percentage (original + bonus) | FR-002 |

---

# 11. Validation Rules

| Rule ID | Field / Input / Action | Validation Rule | Expected Error |
| ------- | ---------------------- | --------------- | -------------- |
| VAL-001 | model_id | Required, non-empty string; alphanumeric + hyphens only | "Model ID is required" / "Model ID can only contain letters, numbers, and hyphens" |
| VAL-002 | model_name | Required, non-empty string | "Model name is required" |
| VAL-003 | trm_official_cop | Required, must be > 0 | "TRM Official COP must be greater than 0" |
| VAL-004 | btk_trm_cop | Required, must be > 0 | "BTK TRM COP must be greater than 0" |
| VAL-005 | tokens | Must be ≥ 0 (integer) | "Tokens cannot be negative" / "Tokens must be greater than 0" |
| VAL-006 | percentage | Must be between 0 and 100% (0.0–1.0 after normalization) | "Percentage must be between 0 and 1" |
| VAL-007 | previous_fortnight_usd | Must be ≥ 0 | "Previous Fortnight USD cannot be negative" |
| VAL-008 | fines_count | Must be ≥ 0 | "Fines count cannot be negative" |
| VAL-009 | custom_fine_cop | Must be ≥ 0 | "Custom fine amount cannot be negative" |
| VAL-010 | advances[].amount | Each must be ≥ 0 | "Advance N amount cannot be negative" |
| VAL-011 | extras[].amount | Each must be ≥ 0 | "Extra N amount cannot be negative" |
| VAL-012 | other_sites[].amount | Each must be ≥ 0 | "Other Site N amount cannot be negative" |
| VAL-013 | other_sites[].site_type | Must be "USD" or "TKS" | "Other Site N type must be USD or TKS" |
| VAL-014 | Date fields | Must match YYYY-MM-DD format | "Date must be in YYYY-MM-DD format" |
| VAL-015 | File paths | Must not contain null bytes or path traversal (`..`) | Invalid filepath rejected |
| VAL-016 | Filename characters | Forbidden chars (`<>:"/\|?*\x00-\x1F`) replaced with `_` | Filename sanitized automatically |

---

# 12. Error Handling Requirements

| Error ID | Condition | Expected System Behavior | Related Requirement |
| -------- | --------- | ------------------------ | ------------------- |
| ERR-001  | Validation fails on any input field | Error list returned; messagebox displayed to user | FR-020, VAL-001 through VAL-014 |
| ERR-002  | Calculation encounters invalid data | `CalculationError` raised; messagebox shown | FR-001 |
| ERR-003  | Vault decryption fails (wrong/missing key) | `VaultError` raised with "Cannot decrypt vault (invalid key)" | FR-011, FR-012 |
| ERR-004  | File not found in vault during retrieval | `VaultError` raised with "File not found in vault: {name}" | FR-013 |
| ERR-005  | `cryptography` package not installed | `ConfigurationError` raised; vault features disabled; label shown in UI | FR-011 |
| ERR-006  | Configuration file not found | `ConfigurationError` raised; application exits with error message | — |
| ERR-007  | PDF generation fails (disk full, permission) | `ReceiptGenerationError` raised; messagebox shown | FR-010 |
| ERR-008  | File I/O operations fail (save, copy, move, delete) | `StorageError` raised with descriptive message | FR-013, FR-014, FR-015 |
| ERR-009  | GUI initialization fails | Application exits with error message shown via messagebox | — |
| ERR-010  | PDF preview cannot open file (corrupt PDF, missing file) | Returns `False`; messagebox shows error | FR-016 |

---

# 13. UI Requirements

Use only if the system has a user interface.

| ID     | Requirement      | Screen / Component | Acceptance Criteria |
| ------ | ---------------- | ------------------ | ------------------- |
| UI-001 | The system shall provide a 3-tab interface (Main, Vault, Admin) | `ttk.Notebook` in `window_setup.py` | Three tabs visible and navigable |
| UI-002 | The system shall display input fields for: model ID, model name, TRM Official, BTK TRM, tokens, percentage, other sites, previous fortnight USD, advances, extras, fines | `main_tab_ui.py:_create_input_fields()` | All fields rendered with labels; percentage as dropdown (60%/70%/75%) |
| UI-003 | The system shall display two receipt panels side by side: Full Receipt (left) and Payment Confirmation (right) | `main_tab_ui.py:_create_receipt_displays()` | Both `tk.Text` widgets displayed after calculation |
| UI-004 | The system shall dynamically add/remove advances, extras, and other-site rows with "X" delete buttons | `add_advance_field()`, `add_extra_field()`, `add_other_site_field()` | New row appears; "X" removes it; at least 1 row always present |
| UI-005 | The system shall provide vault management: listbox, Export Selected, Delete Selected, Import PDFs, Refresh, Toggle Resolution buttons | `vault_tab_ui.py:_create_vault_tab()` | All buttons functional; listbox populated with vault entries |
| UI-006 | The system shall provide PDF preview in vault tab with canvas, zoom dropdown (50%–200%), page navigation (Previous/Next), page counter | `vault_tab_ui.py:_create_pdf_preview_in_vault()` | PDF renders on canvas; zoom/prev/next change display |
| UI-007 | The system shall provide admin COP-to-USD calculator with TRM Official, BTK TRM, Desired COP inputs and results display | `admin_tab_ui.py:_create_admin_tab()` | Inputs accept values; "Calculate Required USD" shows breakdown |
| UI-008 | The system shall show a fee breakdown reference in the admin tab | `admin_tab_ui.py:_create_admin_tab()` notes_frame | Static text displayed: 4% retention tax, transfer fee details |
| UI-009 | The system shall provide checkboxes for "Always apply -300 TRM" and "Disable All Bonuses" | `main_tab_ui.py:_create_input_fields()` row 128-145 | Checkboxes toggle behavior in calculation |
| UI-010 | The system shall support resolution toggle (1920×1080 / 1366×768) scaling all UI elements | `resolution_manager.py:ResolutionManager` | Fonts, widgets, spacing scale proportionally |
| UI-011 | The system shall disable/enable fines fields based on percentage selection | `main_tab_ui.py:on_percentage_change()` | ≤60%: fines enabled; >60%: fines disabled, label changes |
| UI-012 | The system shall scroll the input area independently of receipt panels | Canvas with scrollbar in `main_tab_ui.py` | Mousewheel scrolls input area when hovered |
| UI-013 | The system shall clean up temporary files on exit | `main_window.py:_on_close()` | Temp files from `temp_files` set deleted before destroy |

## 13.1 Screen Definitions

| Screen ID | Screen Name | Purpose | Visible Data | Allowed Actions |
| --------- | ----------- | ------- | ------------ | --------------- |
| SCR-001   | Main Tab | Primary payment calculation interface | Input fields, full receipt, payment confirmation | Calculate, Clear Fields, Save Model Image, Save PDF |
| SCR-002   | Vault Tab | Encrypted vault management | Vault entries list (filename, index), PDF preview canvas, vault stats (count, size) | Export Selected, Delete Selected, Import PDFs, Refresh, Toggle Resolution, PDF Preview (zoom, navigate) |
| SCR-003   | Admin Tab | COP-to-USD reverse calculator | TRM Official, BTK TRM, Desired COP inputs; Required USD, Retention Tax, Transfer Fee results | Calculate Required USD, Exit |

---

# 14. API Requirements

Use only if the system exposes or consumes APIs.

## 14.1 Endpoint Format

| Field                   | Value                             |
| ----------------------- | --------------------------------- |
| Endpoint ID             | API-001                           |
| Method                  | GET / POST / PUT / PATCH / DELETE |
| Route                   |                                   |
| Authentication Required | Yes / No                          |
| Request Body            |                                   |
| Response Body           |                                   |
| Success Status          |                                   |
| Error Statuses          |                                   |
| Related Requirements    |                                   |

## 14.2 API Endpoints

| ID      | Method | Route | Expected Behavior | Related Requirement |
| ------- | ------ | ----- | ----------------- | ------------------- |
|         |        |       | _Not applicable — desktop application with no external API_ | |

---

# 15. API Traceability Matrix

| API ID | Method | Route | Related User Story | Related Use Case | Related Functional Requirement | Related Business Rule | Related Validation Rule | Related Security Requirement | Related Test Case | Status |
| ------ | ------ | ----- | ------------------ | ---------------- | ------------------------------ | --------------------- | ----------------------- | ---------------------------- | ----------------- | ------ |
|        |        |       | _Not applicable — desktop application with no external API_ | | | | | | | |

**Traceability Rules:**
- Every API endpoint must trace to at least one user story, use case, functional requirement, and test case.
- Security-sensitive endpoints must also trace to at least one security requirement.
- Input-handling endpoints must also trace to at least one validation rule.

---

# 16. Data Requirements

## 16.1 Data Entities

| Entity | Purpose |
| ------ | ------- |
| PaymentData | Holds all payment calculation inputs (model info, TRM, tokens, percentage, other sites, advances, extras, fines, flags) |
| CalculationResult | Holds all payment calculation outputs (totals, breakdowns, bonus info, platform USD) |
| Advance | Dated monetary amount for advance payments (deductions) or extras (additions) |
| OtherSite | External platform earnings with type (USD/TKS) and amount |
| VaultEntry | Metadata for a file stored in the encrypted vault (vault filename, original filename, model info, timestamps) |
| VaultIndex | JSON array persisted as `vault_index.json.enc` — list of VaultEntry metadata dicts |
| config.yaml | Runtime configuration: app settings, UI defaults, calculation constants, storage paths |

## 16.2 Data Dictionary

| Field | Type | Required | Meaning | Validation Rule |
| ----- | ---- | -------- | ------- | --------------- |
| model_id | str | Yes | Unique model identifier | Alphanumeric + hyphens only |
| model_name | str | No | Display name for the model | Text, optional |
| trm_official_cop | float | Yes | Official Colombian exchange rate (TRM) | > 0 |
| btk_trm_cop | float | Yes | BroadSpec Token TRM exchange rate | > 0 |
| tokens | int | Yes | Number of TKS tokens earned | ≥ 0 |
| percentage | float | Yes | Model's share of token value (0.6, 0.7, 0.75) | 0 < p ≤ 1 |
| previous_fortnight_usd | float | No | USD carried over from prior period | ≥ 0, default 0 |
| other_sites | List[OtherSite] | No | External platform earnings | site_type in {USD, TKS}, amount ≥ 0 |
| other_sites[].site_type | str | Yes | Currency type: "USD" or "TKS" | Enum: USD, TKS |
| other_sites[].amount | float | Yes | Earnings amount | ≥ 0 |
| advances | List[Advance] | No | Pre-payment deductions | amount ≥ 0, date in YYYY-MM-DD |
| advances[].date | str | Yes | Date of advance | YYYY-MM-DD format |
| advances[].amount | float | Yes | COP amount advanced | ≥ 0 |
| extras | List[Advance] | No | Additional payments to add | amount ≥ 0, date in YYYY-MM-DD |
| fines_count | int | No | Number of fines (30k COP each) | ≥ 0, default 0 |
| custom_fine_cop | float | No | Custom fine amount (overrides fines_count if > 0) | ≥ 0, default 0 |
| override_high_tokens_trm | bool | No | Force -300 TRM adjustment regardless of token count | default False |
| disable_bonus | bool | No | Suppress all bonus calculations | default False |
| bonus_tokens | float | No | Tokens eligible for bonus (0 = all tokens) | ≥ 0, default 0 |
| total_cop | float | Output | Final payment amount in COP | Calculated |
| total_usd | float | Output | Final payment amount in USD | Calculated |
| trm_broadspec_cop | float | Output | Adjusted TRM used for calculation | Calculated |
| transfer_cost_cop | float | Output | Transfer fee in COP | Calculated |
| valor_broadspec_cop | float | Output | BroadSpec value before deductions | Calculated |
| fines_total | float | Output | Total fines deducted | Calculated |
| advances_total | float | Output | Total advances deducted | Calculated |
| extras_total | float | Output | Total extras added | Calculated |
| usd_from_tokens | float | Output | USD value of main tokens | Calculated |
| net_usd | float | Output | USD from tokens × final percentage | Calculated |
| usd_to_send_platform | float | Output | USD to transfer to platform | Calculated |
| bonus_percentage | float | Output | Bonus rate from tier lookup | Calculated |
| bonus_amount_usd | float | Output | Extra USD from bonus | Calculated |
| bonus_amount_cop | float | Output | Extra COP from bonus | Calculated |
| original_percentage | float | Output | Base percentage before bonus | Input |
| final_percentage | float | Output | Percentage after bonus applied | Calculated |
| total_tokens_all_sites | float | Output | Combined token total all sources | Calculated |

## 16.3 Data Storage Rules

| ID     | Requirement      |
| ------ | ---------------- |
| DR-001 | The system shall store receipt PDFs exclusively in the encrypted vault (`single_vault.zip.enc`), not as local files |
| DR-002 | The system shall store vault metadata in an encrypted JSON index (`vault_index.json.enc`) |
| DR-003 | The system shall generate the encryption key on first run and persist it in `.secure_store/key.key` |
| DR-004 | The system shall use Fernet symmetric encryption for all vault and index files |
| DR-005 | The system shall load runtime configuration from `config.yaml` at startup |
| DR-006 | The system shall create the vault directory (`.secure_store/`) and key on first initialization |
| DR-007 | The system shall save model receipt screenshots as JPEG in `img/` directory |
| DR-008 | Temporary files (PDF preview) shall be tracked in `temp_files` set and cleaned up on exit |

## 16.4 Data Integrity Rules

| ID     | Rule |
| ------ | ---- |
| DI-001 | Vault ZIP contents must match vault index entries; `rebuild_index_from_vault()` regenerates index from ZIP |
| DI-002 | Vault operations (add, delete) must update both the encrypted ZIP and the encrypted index atomically |
| DI-003 | Filenames in vault must be sanitized (forbidden characters replaced, trailing spaces/dots stripped) |
| DI-004 | File paths must be validated against path traversal and null byte injection |
| DI-005 | Vault index must be decryptable with the same key as the vault file |

---

# 17. Security Requirements

| ID      | Requirement         | Verification Method |
| ------- | ------------------- | ------------------- |
| SEC-001 | The system shall encrypt all vault contents using Fernet symmetric encryption | Unit tests verify encrypt/decrypt roundtrip; key stored in `.secure_store/key.key` |
| SEC-002 | The system must not store encryption keys in plaintext outside `.secure_store/` | `key.key` excluded from git via `.gitignore` |
| SEC-003 | The system shall validate file paths against null byte injection | `file_operations.py:validate_filepath()` rejects `\x00` characters |
| SEC-004 | The system shall prevent path traversal attacks in file operations | `file_operations.py:validate_filepath()` rejects `..` segments |
| SEC-005 | The system shall sanitize filenames (remove `<>:"/\|?*\x00-\x1F`, trim trailing spaces/dots) | `sanitize_filename()` in both `formatters.py` and `vault_manager.py` |
| SEC-006 | The system must not expose BTK TRM in model receipt screenshots | `model_image_saver.py` filters lines containing "btk" (case-insensitive) |
| SEC-007 | The system shall clean up temporary files (PDF preview, receipts) on application exit | `main_window.py:_on_close()` deletes all paths in `temp_files` set |
| SEC-008 | The system shall show an error when vault decryption fails (wrong key) rather than exposing raw encrypted data | `VaultError` raised with message "Cannot decrypt vault (invalid key)" |

---

# 18. Compliance Requirements

Use only when checking legal, institutional, rubric, security, privacy, or technical compliance.

| ID       | Compliance Rule | Required System Behavior | Evidence Needed |
| -------- | --------------- | ------------------------ | --------------- |
|          | _Not applicable — no formal compliance regime required for this local desktop application_ | | |

---

# 19. Non-Functional Requirements

## 19.1 Performance

| ID       | Requirement      | Measurement |
| -------- | ---------------- | ----------- |
| PERF-001 | Payment calculation shall complete within 100ms for typical input | Unit test timing; no async operations needed |
| PERF-002 | PDF preview shall render the first page within 2 seconds | PyMuPDF renders on demand; zoom levels cached |
| PERF-003 | Vault operations (add, retrieve, delete) shall complete within 500ms for files up to 10MB | Synchronous file I/O, measured locally |

## 19.2 Reliability

| ID      | Requirement      | Measurement |
| ------- | ---------------- | ----------- |
| REL-001 | Vault additions shall be atomic (both ZIP and index updated or neither) | Index saved immediately after ZIP update |
| REL-002 | The system shall not lose payment data if calculation is performed before saving | Results held in memory (`current_input_data`, `current_result_data`) until explicit save |
| REL-003 | The system shall handle graceful degradation when optional dependencies are missing (cryptography → vault disabled, PyMuPDF → preview disabled) | Try/except on imports; feature flags checked at runtime |

## 19.3 Maintainability

| ID      | Requirement      | Verification |
| ------- | ---------------- | ------------ |
| MNT-001 | The codebase shall maintain ≥80% test coverage | `pytest.ini` enforces `--cov-fail-under=80` |
| MNT-002 | The codebase shall follow MVC architecture pattern | `ApplicationController` (controller), `BroadSpecGUI` (view), `PaymentData`/`CalculationResult` (model) |
| MNT-003 | The codebase shall use Repository pattern for vault operations | `VaultRepository` class abstracts all vault I/O |
| MNT-004 | Business logic shall be separated from UI code | `broadspec/core/` contains zero tkinter imports; `broadspec/ui/` contains only UI code |
| MNT-005 | All exceptions shall extend `BroadSpecError` base class | `exceptions.py` defines hierarchy: BroadSpecError → CalculationError, VaultError, ValidationError, etc. |

## 19.4 Availability

| ID      | Requirement      | Measurement |
| ------- | ---------------- | ----------- |
| AVL-001 | The system shall operate fully offline (no network dependency) | All dependencies are local libraries; no HTTP calls |
| AVL-002 | The system shall start within 5 seconds on supported platforms | Single Tkinter window initialization |

---

# 20. LLM-Specific Requirements

Use only if the software uses an LLM.

## 20.1 LLM Behavior

| ID      | Requirement                                                             | Acceptance Criteria |
| ------- | ----------------------------------------------------------------------- | ------------------- |
|         | _Not applicable — no LLM component in this application_                  | |

## 20.2 Prompt Rules

| ID         | Requirement                                            | Acceptance Criteria |
| ---------- | ------------------------------------------------------ | ------------------- |
|            | _Not applicable — no LLM component_                     | |

## 20.3 Retrieval / RAG Rules

| ID      | Requirement                                                                            | Acceptance Criteria |
| ------- | -------------------------------------------------------------------------------------- | ------------------- |
|         | _Not applicable — no RAG/retrieval component_                                           | |

## 20.4 Hallucination Control

| ID      | Requirement                                                                  | Acceptance Criteria |
| ------- | ---------------------------------------------------------------------------- | ------------------- |
|         | _Not applicable — no LLM component_                                          | |

## 20.5 Prompt Injection Protection

| ID      | Requirement                                                                          | Acceptance Criteria |
| ------- | ------------------------------------------------------------------------------------ | ------------------- |
|         | _Not applicable — no LLM component_                                                  | |

---

# 21. Traceability Matrix

| Requirement ID | Business Rule | API / UI / Data Element | Test Case | Status |
| -------------- | ------------- | ----------------------- | --------- | ------ |
| FR-001 | BR-008, BR-009 | PaymentData, CalculationResult | test_calculate_basic_payment | Pass |
| FR-002 | BR-001, BR-002 | total_tokens_all_sites, bonus_percentage | test_calculate_bonus_percentage_new_structure | Pass |
| FR-003 | BR-001, BR-007 | OtherSite, other_sites_total_usd | test_calculate_bonus_with_other_sites_usd, test_calculate_bonus_with_other_sites_tks, test_calculate_bonus_with_mixed_sites | Pass |
| FR-004 | BR-002 | disable_bonus flag | test_calculate_bonus_disable_bonus_flag | Pass |
| FR-005 | BR-004 | fines_total, show_fines, fines_display | test_calculate_with_fines_studio, test_calculate_with_fines_home_worker, test_calculate_with_custom_fine | Pass |
| FR-006 | BR-003 | trm_broadspec_cop, override_high_tokens_trm | test_calculate_basic_payment (asserts 3700) | Pass |
| FR-007 | BR-008 | advances_total, extras_total | test_calculate_with_advances | Pass |
| FR-008 | BR-005 | transfer_cost_cop | Implicit in test_calculate_basic_payment | Pass |
| FR-009 | BR-007 | usd_to_send_platform | Included in CalculatorResult | Pass |
| FR-010 | — | ReceiptGenerator | test_generate_pdf_success | Pass |
| FR-011 | — | VaultRepository, add_bytes | test_add_file (vault_manager) | Pass |
| FR-012 | — | vault_index.json.enc | test_load_index_with_data, test_save_index | Pass |
| FR-013 | — | export_from_vault, FileOperations | test_retrieve_file | Pass |
| FR-014 | — | delete_files | test_delete_files, test_delete_files_multiple | Pass |
| FR-015 | — | add_file | test_add_file | Pass |
| FR-016 | — | PDFPreviewer | (PDF preview unit tested via component integration) | — |
| FR-017 | — | ModelImageSaver | — (UI component) | — |
| FR-018 | — | AdminTabUI._calculate_usd_amount | — (UI component) | — |
| FR-019 | — | ResolutionManager | — (UI component) | — |
| FR-020 | VAL-001 through VAL-013 | validate_data, validate_payment_data | test_validate_data_valid, test_validate_data_missing_model_id, test_validate_data_negative_values | Pass |
| FR-021 | — | generate_filename | test_generate_filename_with_result | Pass |
| FR-022 | BR-002 | bonus_tokens, bonus_ratio | — (bonus range tests implied by calculator logic) | — |

---

# 22. Acceptance Criteria

| ID      | Acceptance Criterion                                                                 |
| ------- | ------------------------------------------------------------------------------------ |
| ACC-001 | Every mandatory functional requirement shall have at least one related test case.    |
| ACC-002 | Every security requirement shall have verification evidence.                         |
| ACC-003 | Every validation rule shall have positive and negative test coverage.                |
| ACC-004 | Every API requirement shall define success and error behavior.                       |
| ACC-005 | Every LLM-specific behavior requirement shall have evaluation prompts or test cases. |

---

# 23. Architecture Constraints

Purpose:
Defines implementation rules the codebase must follow.

| ID | Constraint | Rationale |
| -- | ---------- | --------- |
| ARC-001 | MVC pattern: `ApplicationController` (controller), `BroadSpecGUI`/components (view), `core/models.py` (model) | Separation of concerns; `engineering_methodologies.md` §2.1 |
| ARC-002 | Repository pattern for vault: `VaultRepository` abstracts all encrypted storage operations | Enables testing with mocks; `engineering_methodologies.md` §2.2 |
| ARC-003 | Business logic must not import tkinter; UI must not contain calculation logic | Clean separation; `core/` has zero tkinter imports |
| ARC-004 | Single-user, single-instance desktop application | No concurrency concerns; no session management |
| ARC-005 | All file I/O goes through `FileOperations` or `VaultRepository` | Centralized error handling, path validation, sanitization |
| ARC-006 | All exceptions extend `BroadSpecError` base class | Consistent error hierarchy for UI messagebox display |
| ARC-007 | Configuration loaded once at startup from `config.yaml` and passed via dependency injection | `config.yaml` → `ApplicationController._load_configuration()` → all components |

---

# 24. Technology Stack Requirements

Purpose:
Defines allowed technologies.

| ID | Technology | Version / Variant | Allowed Use |
| -- | ---------- | ----------------- | ----------- |
| TECH-001 | Python | ≥ 3.8 | Runtime language |
| TECH-002 | tkinter | Standard library | GUI framework |
| TECH-003 | ReportLab | ≥ 4.0.0 | PDF receipt generation (`canvas.Canvas`) |
| TECH-004 | cryptography | ≥ 41.0.0 | Fernet encryption for vault |
| TECH-005 | PyMuPDF (fitz) | ≥ 1.23.0 | PDF preview rendering |
| TECH-006 | Pillow (PIL) | ≥ 10.0.0 | Image creation (model receipt screenshots) |
| TECH-007 | PyYAML | ≥ 6.0 | Configuration file parsing |
| TECH-008 | pytest | ≥ 7.0.0 | Unit testing framework |
| TECH-009 | pytest-cov | ≥ 4.0.0 | Test coverage reporting |
| TECH-010 | pytest-mock | ≥ 3.10.0 | Mocking in tests |
| TECH-011 | setuptools | ≥ 61.0 | Package build |

---

# 25. Code Organization Rules

Purpose:
Defines expected project structure.

| ID | Rule | Pattern |
| -- | ---- | ------- |
| ORG-001 | Core business logic in `broadspec/core/` | `calculator.py`, `models.py`, `receipt_generator.py`, `exceptions.py` |
| ORG-002 | UI components in `broadspec/ui/components/` | `main_tab_ui.py`, `vault_tab_ui.py`, `admin_tab_ui.py`, `calculation_handler.py`, `pdf_saver.py`, `model_image_saver.py`, `resolution_manager.py`, `pdf_preview_handler.py`, `window_setup.py` |
| ORG-003 | Storage layer in `broadspec/storage/` | `vault_manager.py`, `file_operations.py` |
| ORG-004 | Utility functions in `broadspec/utils/` | `formatters.py`, `validators.py`, `pdf_preview.py`, `pdf_protocols.py` |
| ORG-005 | Entry point at `broadspec/main.py` | `main()` initializes `ApplicationController` and starts Tkinter event loop |
| ORG-006 | Tests mirror source structure under `tests/unit/` | `test_calculator.py`, `test_receipt_generator.py`, `test_vault_manager.py`, `test_file_operations.py`, `test_pdf_protocols.py` |
| ORG-007 | Configuration at project root | `config.yaml` |
| ORG-008 | Dependencies tracked in `requirements/` | `base.txt`, `test.txt` |
| ORG-009 | Documentation in `docs/` | `bonusSystem.md`, `srstemplateV1.1.md`, `updates/bonusranges.md` |

Project tree:
```
broadspec/
├── __init__.py
├── main.py                     # Entry point + ApplicationController
├── core/
│   ├── __init__.py
│   ├── calculator.py           # PaymentCalculator
│   ├── models.py               # PaymentData, CalculationResult, VaultEntry, OtherSite, Advance
│   ├── receipt_generator.py    # ReceiptGenerator (PDF)
│   ├── exceptions.py           # BroadSpecError hierarchy
│   └── calculatoranalysys.md   # Original calculation notes
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # BroadSpecGUI (orchestrator)
│   ├── components/
│   │   ├── window_setup.py     # Window initialization, notebook, tabs
│   │   ├── main_tab_ui.py      # Main tab input fields + receipt displays
│   │   ├── vault_tab_ui.py     # Vault management + PDF preview
│   │   ├── admin_tab_ui.py     # COP-to-USD calculator
│   │   ├── calculation_handler.py
│   │   ├── pdf_saver.py
│   │   ├── model_image_saver.py
│   │   ├── resolution_manager.py
│   │   └── pdf_preview_handler.py
│   └── widgets/
│       └── __init__.py         # (placeholder for custom widgets)
├── storage/
│   ├── __init__.py
│   ├── vault_manager.py        # VaultRepository
│   └── file_operations.py      # FileOperations
└── utils/
    ├── __init__.py
    ├── formatters.py           # Currency formatting, filename parsing
    ├── validators.py           # Input validation functions
    ├── pdf_preview.py          # PDFPreviewer (PyMuPDF)
    └── pdf_protocols.py        # Filename generation, sanitization

tests/
├── conftest.py
└── unit/
    ├── test_calculator.py
    ├── test_receipt_generator.py
    ├── test_vault_manager.py
    ├── test_file_operations.py
    └── test_pdf_protocols.py
```

---

# 26. Configuration Requirements

Purpose:
Defines environment configuration.

| ID | Config Key | Required | Secret | Description |
| -- | ---------- | -------- | ------ | ----------- |
| CONFIG-001 | `app.name` | Yes | No | Application display name: "BroadSpec Payment Calculator" |
| CONFIG-002 | `app.version` | Yes | No | Application version string: "0.001" |
| CONFIG-003 | `app.transfer_cost` | Yes | No | Base transfer fee in USD: 6.99 |
| CONFIG-004 | `ui.default_width` | Yes | No | Default window width: 1900 |
| CONFIG-005 | `ui.default_height` | Yes | No | Default window height: 1064 |
| CONFIG-006 | `ui.pdf_preview_enabled` | Yes | No | Enable/disable PDF preview feature: true |
| CONFIG-007 | `ui.resolutions` | Yes | No | Supported display resolutions: 1920×1080 and 1366×768 |
| CONFIG-008 | `ui.themes` | Yes | No | Theme colors: primary, secondary, background, text |
| CONFIG-009 | `storage.vault_path` | Yes | No | Directory for encrypted vault: ".secure_store" |
| CONFIG-010 | `storage.receipts_path` | Yes | No | Directory for exported receipts: "Receipts" |
| CONFIG-011 | `storage.encryption_algorithm` | Yes | No | Encryption method: "Fernet" |
| CONFIG-012 | `calculation.token_to_usd_rate` | Yes | No | TKS to USD conversion rate: 20.0 |
| CONFIG-013 | `calculation.trm_adjustment` | Yes | No | Default COP deduction from TRM: 300 |
| CONFIG-014 | `calculation.fine_amount` | Yes | No | Fine amount per count in COP: 30000 |
| CONFIG-015 | `calculation.transfer_cost_tax` | Yes | No | Tax percentage on transfer cost: 0.19 (19%) |
