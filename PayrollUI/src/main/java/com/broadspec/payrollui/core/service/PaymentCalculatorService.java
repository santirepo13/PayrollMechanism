package com.broadspec.payrollui.core.service;

import com.broadspec.payrollui.core.exception.CalculationException;
import com.broadspec.payrollui.core.exception.ValidationException;
import com.broadspec.payrollui.core.model.CalculationResult;
import com.broadspec.payrollui.core.model.PaymentData;
import com.broadspec.payrollui.util.Validators;

import java.util.List;
import java.util.Map;

public class PaymentCalculatorService {

    private final double tokenToUsdRate;
    private final double trmAdjustment;
    private final double fineAmount;
    private final double transferCost;
    private final double transferCostTax;

    @SuppressWarnings("unchecked")
    public PaymentCalculatorService(Map<String, Object> config) {
        Map<String, Object> calc = (Map<String, Object>) config.getOrDefault("calculation", Map.of());
        Map<String, Object> app  = (Map<String, Object>) config.getOrDefault("app", Map.of());

        this.tokenToUsdRate   = toDouble(calc.get("tokenToUsdRate"), 20.0);
        this.trmAdjustment    = toDouble(calc.get("trmAdjustment"), 300.0);
        this.fineAmount       = toDouble(calc.get("fineAmount"), 30000.0);
        this.transferCostTax  = toDouble(calc.get("transferCostTax"), 0.19);
        this.transferCost     = toDouble(app.get("transferCost"), 6.99);
    }

    public CalculationResult calculate(PaymentData data) {
        List<String> errors = Validators.validatePaymentData(data);
        if (!errors.isEmpty()) {
            throw new ValidationException("Validation failed: " + String.join("; ", errors));
        }

        try {
            return doCalculate(data);
        } catch (Exception e) {
            throw new CalculationException("Payment calculation failed: " + e.getMessage(), e);
        }
    }

    private CalculationResult doCalculate(PaymentData data) {
        double otherSitesTokensTotal = data.otherSites().stream()
            .mapToDouble(site -> site.getTksEquivalent(tokenToUsdRate))
            .sum();
        double totalTokensAllSites = data.tokens() + otherSitesTokensTotal;

        double originalPercentage = data.percentage() > 1
            ? data.percentage() / 100.0
            : data.percentage();

        double bonusTokensUsed, nonBonusTokens, bonusRatio;
        if (data.disableBonus()) {
            bonusTokensUsed = 0;
        } else if (data.bonusTokens() > 0) {
            bonusTokensUsed = Math.min(data.bonusTokens(), totalTokensAllSites);
        } else {
            bonusTokensUsed = totalTokensAllSites;
        }
        nonBonusTokens = totalTokensAllSites - bonusTokensUsed;
        bonusRatio = totalTokensAllSites > 0 ? bonusTokensUsed / totalTokensAllSites : 0;

        double bonusPercentage = data.disableBonus()
            ? 0.0
            : calculateBonusPercentage(bonusTokensUsed);

        double bonusRate = originalPercentage + bonusPercentage;

        double finalPercentage = originalPercentage + bonusRatio * bonusPercentage;

        double trmAdjustmentUsed = data.overrideHighTokensTrm()
            ? trmAdjustment
            : (totalTokensAllSites >= 3000 ? 200 : trmAdjustment);
        double trmBroadspecCop = data.trmOfficialCop() - trmAdjustmentUsed;

        double transferCostUsd = transferCost + (transferCost * transferCostTax);
        double transferCostCop = transferCostUsd * data.btkTrmCop();

        double usdFromTokens = data.tokens() / tokenToUsdRate;
        double netUsd = usdFromTokens * finalPercentage;

        double otherSitesTotalUsdRaw = data.otherSites().stream()
            .mapToDouble(site -> site.getUsdEquivalent(tokenToUsdRate))
            .sum();
        double otherSitesTotalUsd = otherSitesTotalUsdRaw * finalPercentage;

        double totalUsdPrecalc = netUsd + otherSitesTotalUsd + data.previousFortnightUsd();
        double valorBroadspecCop = (totalUsdPrecalc * trmBroadspecCop) - transferCostCop;

        Fines fines = calculateFines(data);
        double advancesTotal = data.advances().stream().mapToDouble(a -> a.amount()).sum();
        double extrasTotal = data.extras().stream().mapToDouble(a -> a.amount()).sum();

        double totalCopBase = valorBroadspecCop - advancesTotal - fines.total + extrasTotal;
        double lowIncomeReimbursementCop = data.belowBtkThreshold() ? transferCostCop : 0.0;
        double totalCop = totalCopBase + lowIncomeReimbursementCop;
        double totalUsd = totalCop / trmBroadspecCop;

        double totalUsdRaw = usdFromTokens + otherSitesTotalUsdRaw;
        double bonusAmountUsd = totalUsdRaw * bonusRatio * bonusPercentage;
        double bonusAmountCop = bonusAmountUsd * trmBroadspecCop;

        double tokenValueCop = data.btkTrmCop() * 0.05;
        double usdToSendPlatform = (tokenValueCop > 0 && tokenToUsdRate > 0)
            ? ((totalCopBase + transferCostCop) / tokenValueCop) / tokenToUsdRate
            : 0.0;

        return CalculationResult.builder()
            .totalCop(totalCop)
            .totalUsd(totalUsd)
            .trmBroadspecCop(trmBroadspecCop)
            .transferCostCop(transferCostCop)
            .valorBroadspecCop(valorBroadspecCop)
            .finesTotal(fines.total)
            .finesDisplay(fines.display)
            .showFines(fines.showFines)
            .advancesTotal(advancesTotal)
            .extrasTotal(extrasTotal)
            .otherSitesTotalUsd(otherSitesTotalUsd)
            .usdFromTokens(usdFromTokens)
            .netUsd(netUsd)
            .totalUsdPrecalc(totalUsdPrecalc)
            .usdToSendPlatform(usdToSendPlatform)
            .btkTrmCop(data.btkTrmCop())
            .totalTokensAllSites(totalTokensAllSites)
            .bonusPercentage(bonusPercentage)
            .bonusAmountUsd(bonusAmountUsd)
            .bonusAmountCop(bonusAmountCop)
            .originalPercentage(originalPercentage)
            .finalPercentage(finalPercentage)
            .bonusTokensUsed(bonusTokensUsed)
            .nonBonusTokens(nonBonusTokens)
            .bonusRatio(bonusRatio)
            .bonusRate(bonusRate)
            .lowIncomeReimbursementCop(lowIncomeReimbursementCop)
            .build();
    }

    private double calculateBonusPercentage(double totalTokens) {
        if (totalTokens >= 20000) return 0.10;
        if (totalTokens >= 17500) return 0.08;
        if (totalTokens >= 15000) return 0.06;
        if (totalTokens >= 12500) return 0.045;
        if (totalTokens >= 10000) return 0.03;
        return 0.0;
    }

    private Fines calculateFines(PaymentData data) {
        double percent = data.percentage() > 1 ? data.percentage() / 100.0 : data.percentage();
        boolean showFines = percent <= 0.60;

        if (data.customFineCop() > 0) {
            return new Fines(data.customFineCop(),
                String.format("Custom: %,.0f COP", data.customFineCop()), showFines);
        }

        double total = data.finesCount() * fineAmount;
        return new Fines(total,
            String.format("%d fines x %,.0f = %,.0f COP", data.finesCount(), fineAmount, total),
            showFines);
    }

    private record Fines(double total, String display, boolean showFines) {}

    private static double toDouble(Object value, double defaultValue) {
        if (value instanceof Number n) return n.doubleValue();
        if (value instanceof String s) {
            try { return Double.parseDouble(s); } catch (NumberFormatException ignored) {}
        }
        return defaultValue;
    }
}
