# BroadSpec Bonus System

## Purpose

The bonus system rewards models for higher token production across all sites (BroadSpec + external sites). As cumulative token volume increases, a bonus percentage is added on top of the model's base payment percentage.

---

## Bonus Tiers

Bonus rate is determined by **total tokens across all sites** (main BroadSpec tokens + other sites converted to TKS equivalent).

| Tier | Token Threshold | Bonus % | Rate |
|------|----------------|---------|------|
| 1    | 10,000+        | 3.0%    | 0.03 |
| 2    | 12,500+        | 4.5%    | 0.045 |
| 3    | 15,000+        | 6.0%    | 0.06 |
| 4    | 17,500+        | 8.0%    | 0.08 |
| 5    | 20,000+        | 10.0%   | 0.10 |

Below 10,000 tokens: no bonus.

Source: `broadspec/core/calculator.py:_calculate_bonus_percentage()` (line 125)

---

## Token Aggregation

Total tokens = **main tokens (TKS)** + **other sites** (converted to TKS):

| Source | Conversion |
|--------|-----------|
| Main Tokens | Direct TKS value |
| Other Sites (USD) | `amount × token_to_usd_rate` (20 TKS per USD) |
| Other Sites (TKS) | Direct TKS value |

The `token_to_usd_rate` (20.0) is defined in `config.yaml:31`.

---

## Calculation Flow

### Standard mode (all tokens qualify for bonus)

```
total_tokens_all_sites   = main_tokens + other_sites_tokens
bonus_percentage         = get_tier(total_tokens_all_sites)
final_percentage         = original_percentage + bonus_percentage

total_usd_raw            = usd_from_tokens + other_sites_total_usd_raw
bonus_amount_usd         = total_usd_raw × bonus_percentage
```

### Bonus token range mode (user caps which tokens get bonus)

```
bonus_tokens_used = min(bonus_tokens_input, total_tokens_all_sites)  if bonus_tokens_input > 0
                    total_tokens_all_sites                           if bonus_tokens_input = 0
non_bonus_tokens = total_tokens_all_sites - bonus_tokens_used
bonus_ratio      = bonus_tokens_used / total_tokens_all_sites

final_percentage = original_percentage + bonus_ratio × bonus_percentage
bonus_amount_usd = total_usd_raw × bonus_ratio × bonus_percentage
```

This allows the user to specify only the tokens earned within a **fortnight (2-week) range** as eligible for bonus, while still applying the base percentage to all tokens.

---

## Data Model

### Input — `PaymentData` (`broadspec/core/models.py:32`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tokens` | `int` | — | Main BroadSpec tokens |
| `other_sites` | `List[OtherSite]` | `[]` | External site earnings |
| `bonus_tokens` | `float` | `0.0` | Tokens eligible for bonus (0 = all) |
| `disable_bonus` | `bool` | `False` | Master toggle to disable all bonus |

### Output — `CalculationResult` (`broadspec/core/models.py:59`)

| Field | Type | Description |
|-------|------|-------------|
| `total_tokens_all_sites` | `float` | Combined token total |
| `bonus_percentage` | `float` | Bonus rate from tier lookup |
| `bonus_tokens_used` | `float` | Tokens that actually received bonus |
| `non_bonus_tokens` | `float` | Tokens that did not receive bonus |
| `bonus_ratio` | `float` | `bonus_tokens_used / total_tokens` |
| `bonus_amount_usd` | `float` | Extra USD earned from bonus |
| `bonus_amount_cop` | `float` | Extra COP earned from bonus |
| `original_percentage` | `float` | Base percentage before bonus |
| `final_percentage` | `float` | Weighted percentage after bonus |

---

## UI Elements (`broadspec/ui/components/main_tab_ui.py`)

### Input Form

- **Total Tokens (All Sites):** read-only label updated live as user types
- **Tokens for Bonus (TKS):** numeric entry, default `"0"` (use all tokens)
- **Disable All Bonuses:** checkbox to suppress bonus entirely

### Receipts

**Full Receipt** shows:
- Token breakdown (bonus vs non-bonus)
- Tier and percentage applied
- Bonus amount earned

**Payment Confirmation** shows:
- Final percentage
- Bonus line (when active)

---

## Configuration (`config.yaml`)

```yaml
calculation:
  token_to_usd_rate: 20.0    # USD → TKS conversion
```

Bonus tiers are **not configurable** — they are hardcoded in the calculator.

---

## File Map

| File | Role |
|------|------|
| `broadspec/core/calculator.py` | Bonus tier logic, weighted calculation |
| `broadspec/core/models.py` | `PaymentData`, `CalculationResult` data classes |
| `broadspec/main.py` | Controller — data conversion and wiring |
| `broadspec/ui/components/main_tab_ui.py` | Input form widgets, live total display |
| `broadspec/ui/components/calculation_handler.py` | Receipt generation, form data collection |
| `config.yaml` | `token_to_usd_rate` for USD→TKS conversion |
| `tests/unit/test_calculator.py` | Unit tests for bonus calculation |
| `docs/updates/bonusranges.md` | Feature specification for bonus token ranges |

---

## History

| Date | Change |
|------|--------|
| 2026-03-02 | Original bonus system — 7 tiers (15k–30k, 2.5%–10%) |
| 2026-05-11 | Restructured to 5 lower tiers (10k–20k, 3%–10%) |
| 2026-06-01 | Added bonus token range selection — user can cap which tokens get bonus |
