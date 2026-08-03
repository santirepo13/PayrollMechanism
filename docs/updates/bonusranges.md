# Bonus Token Ranges — Feature Specification

## Overview

Currently the bonus system applies the bonus percentage (3%–10%) to **all** tokens across all sites. Since bonuses are meant to reward tokens earned within a **2-week (fortnight) period**, but models request payment on arbitrary dates, this feature allows the user to manually specify which portion of the total tokens should qualify for the bonus.

## Changes Summary

| # | Area | Change |
|---|------|--------|
| 1 | **UI** | Add live "Total Tokens (All Sites)" read-only display in the input form |
| 2 | **UI** | Add "Tokens for Bonus (TKS)" numeric entry field in the input form |
| 3 | **Models** | New `bonus_tokens` field on `PaymentData` |
| 4 | **Models** | New result fields: `bonus_tokens_used`, `non_bonus_tokens`, `bonus_ratio` on `CalculationResult` |
| 5 | **Calculator** | Split calculation into bonus / non-bonus portions using a weighted average |
| 6 | **Receipts** | Both Full Receipt and Payment Confirmation show the breakdown |
| 7 | **Controller** | Wire new fields through all conversion methods |

---

## 1. UI — Input Form (`main_tab_ui.py`)

### New widgets

Inserted between the "Other Sites" section and the "Previous Fortnight USD" section:

```
┌─────────────────────────────────────────────┐
│ Other Sites (USD or TKS):                   │
│   [USD] [__________]  [X]                   │
│   [+ Add Other Site]                        │
│                                              │
│ Total Tokens (All Sites):    12,500 TKS     │  ← NEW: read-only, bold
│                                              │
│ Tokens for Bonus (TKS):     [___________]   │  ← NEW: entry, default "0"
│                                              │
│ Previous Fortnight USD:     [___________]   │
└─────────────────────────────────────────────┘
```

### Style

| Widget | Font | Width | Padding | Sticky |
|--------|------|-------|---------|--------|
| Label (Total) | `('Arial', 10)` | — | `pady=5` | `tk.W` |
| Value (Total) | `('Arial', 10, 'bold')` | — | `pady=5` | `(tk.W, tk.E)` |
| Label (Bonus) | `('Arial', 10)` | — | `pady=5` | `tk.W` |
| Entry (Bonus) | default | `20` | `pady=5` | `(tk.W, tk.E)` |

### Live total update

- `<KeyRelease>` bound to the main Tokens entry and each Other Site amount entry
- `<<ComboboxSelected>>` bound to each Other Site type combo (USD / TKS)
- Conversion: USD × 20 = TKS (mirrors `token_to_usd_rate` in `config.yaml`)
- `_update_total_display()` recomputes and updates the read-only label text
- The "Tokens for Bonus" field defaults to `"0"` (meaning: use all tokens — backward compatible)

---

## 2. Data Models (`models.py`)

### `PaymentData` — new field

```python
@dataclass
class PaymentData:
    ...
    bonus_tokens: float = 0.0
```

- `0.0` = use all tokens for bonus (backward compatible)
- `> 0` = cap bonus to this many tokens

### `CalculationResult` — new fields

```python
@dataclass
class CalculationResult:
    ...
    bonus_tokens_used: float = 0.0
    non_bonus_tokens: float = 0.0
    bonus_ratio: float = 0.0
```

---

## 3. Calculator Logic (`calculator.py`)

### Current behavior (simplified)

```python
total_tokens_all_sites = main_tokens + other_sites_tokens
bonus_percentage = get_tier(total_tokens_all_sites)
final_percentage = original_percentage + bonus_percentage
net_usd = total_usd_raw * final_percentage
```

Every token receives the full bonus. No split.

### New behavior

```python
total_tokens_all_sites = main_tokens + other_sites_tokens     # unchanged
bonus_percentage = get_tier(total_tokens_all_sites)            # unchanged

# Determine which tokens get the bonus
if disable_bonus:
    bonus_tokens_used = 0
elif data.bonus_tokens > 0:
    bonus_tokens_used = min(data.bonus_tokens, total_tokens_all_sites)
else:
    bonus_tokens_used = total_tokens_all_sites                 # backward compatible

non_bonus_tokens = total_tokens_all_sites - bonus_tokens_used
bonus_ratio = bonus_tokens_used / total_tokens_all_sites       # fraction

# Weighted final percentage
final_percentage = original_percentage + bonus_ratio * bonus_percentage

# The bonus amount (extra earned)
total_usd_raw = usd_from_tokens + other_sites_total_usd_raw
bonus_amount_usd = total_usd_raw * bonus_ratio * bonus_percentage
bonus_amount_cop = bonus_amount_usd * trm_broadspec_cop

# For receipt display breakdown
non_bonus_usd = total_usd_raw * (1 - bonus_ratio) * original_percentage
bonus_portion_usd = total_usd_raw * bonus_ratio * (original_percentage + bonus_percentage)
```

### Mathematical identity

```
net_usd = non_bonus_usd + bonus_portion_usd
       = total_usd_raw × (1 - ratio) × original
         + total_usd_raw × ratio × (original + bonus)
       = total_usd_raw × (original + ratio × bonus)
```

---

## 4. Receipts (`calculation_handler.py`)

### Full Receipt — `_generate_full_receipt()`

New section replacing the old BONUS INFORMATION block:

```
BONUS INFORMATION:
  Total Tokens (All Sites): 12,500 TKS
  Bonus Tier: +3.0%
  Non-Bonus Tokens: 2,500 TKS × 60.0% = ...
  Bonus Tokens:     10,000 TKS × 63.0% (60% + 3%) = ...
  Bonus Amount Earned: +... USD (... COP)
  Original Percentage: 60.0%
  Final Percentage: 62.4%
```

The `CALCULATED VALUES` section remains the same but `Net Amount USD` now reflects the weighted calculation.

### Model Receipt / Payment Confirmation — `_generate_model_receipt()`

If bonus is active:

```
Percentage: 62.4%
Bonus: +3.0% (on 10,000 TKS)
```

---

## 5. Controller Wiring (`main.py`)

All three conversion methods updated:

| Method | Change |
|--------|--------|
| `_form_data_to_payment_data()` | Pass `bonus_tokens=form_data.get('bonus_tokens', 0)` |
| `_payment_data_to_dict()` | Add `'bonus_tokens': getattr(data, 'bonus_tokens', 0)` |
| `_dict_to_payment_data()` | Add `bonus_tokens=data_dict.get('bonus_tokens', 0)` |
| `_calculation_result_to_dict()` | Add `'bonus_tokens_used'`, `'non_bonus_tokens'`, `'bonus_ratio'` |
| `_dict_to_calculation_result()` | Add `bonus_tokens_used`, `non_bonus_tokens`, `bonus_ratio` |

---

## 6. Backward Compatibility

| Scenario | Behavior |
|----------|----------|
| `bonus_tokens = 0` (default) | All tokens count for bonus → identical to current behavior |
| `bonus_tokens > total` | Capped at total |
| `disable_bonus = True` | Bonus is 0, regardless of `bonus_tokens` |
| Old serialized data (no `bonus_tokens` field) | `getattr/bonus_tokens` returns 0 → full backward compat |

---

## 7. Files Modified

| File | Lines Affected | Type |
|------|---------------|------|
| `broadspec/core/models.py` | `PaymentData` +1 field, `CalculationResult` +3 fields | Add |
| `broadspec/core/calculator.py` | `calculate()` — weighted bonus logic | Modify |
| `broadspec/ui/components/main_tab_ui.py` | `_create_input_fields()` — 2 new rows, `add_other_site_field()` — bindings, new methods `_compute_total_tokens()`, `_update_total_display()`, `clear_fields()` update | Modify |
| `broadspec/ui/components/calculation_handler.py` | `_get_form_data()` — collect bonus_tokens, both receipt generators | Modify |
| `broadspec/main.py` | All 5 conversion methods | Modify |
| `tests/unit/test_calculator.py` | Bonus amount assertions, new tests for `bonus_tokens` parameter | Modify |
