package com.broadspec.payrollui.core.model;

import java.time.LocalDate;

public class CalculationResult {
    private final double totalCop;
    private final double totalUsd;
    private final double trmBroadspecCop;
    private final double transferCostCop;
    private final double valorBroadspecCop;
    private final double finesTotal;
    private final String finesDisplay;
    private final boolean showFines;
    private final double advancesTotal;
    private final double extrasTotal;
    private final double otherSitesTotalUsd;
    private final double usdFromTokens;
    private final double netUsd;
    private final double totalUsdPrecalc;
    private final double usdToSendPlatform;
    private final double btkTrmCop;
    private final String date;
    private final double totalTokensAllSites;
    private final double bonusPercentage;
    private final double bonusAmountUsd;
    private final double bonusAmountCop;
    private final double originalPercentage;
    private final double finalPercentage;
    private final double bonusTokensUsed;
    private final double nonBonusTokens;
    private final double bonusRatio;
    private final double bonusRate;
    private final double lowIncomeReimbursementCop;

    private CalculationResult(Builder builder) {
        this.totalCop = builder.totalCop;
        this.totalUsd = builder.totalUsd;
        this.trmBroadspecCop = builder.trmBroadspecCop;
        this.transferCostCop = builder.transferCostCop;
        this.valorBroadspecCop = builder.valorBroadspecCop;
        this.finesTotal = builder.finesTotal;
        this.finesDisplay = builder.finesDisplay;
        this.showFines = builder.showFines;
        this.advancesTotal = builder.advancesTotal;
        this.extrasTotal = builder.extrasTotal;
        this.otherSitesTotalUsd = builder.otherSitesTotalUsd;
        this.usdFromTokens = builder.usdFromTokens;
        this.netUsd = builder.netUsd;
        this.totalUsdPrecalc = builder.totalUsdPrecalc;
        this.usdToSendPlatform = builder.usdToSendPlatform;
        this.btkTrmCop = builder.btkTrmCop;
        this.date = (builder.date != null && !builder.date.isEmpty())
            ? builder.date : LocalDate.now().toString();
        this.totalTokensAllSites = builder.totalTokensAllSites;
        this.bonusPercentage = builder.bonusPercentage;
        this.bonusAmountUsd = builder.bonusAmountUsd;
        this.bonusAmountCop = builder.bonusAmountCop;
        this.originalPercentage = builder.originalPercentage;
        this.finalPercentage = builder.finalPercentage;
        this.bonusTokensUsed = builder.bonusTokensUsed;
        this.nonBonusTokens = builder.nonBonusTokens;
        this.bonusRatio = builder.bonusRatio;
        this.bonusRate = builder.bonusRate;
        this.lowIncomeReimbursementCop = builder.lowIncomeReimbursementCop;
    }

    public double totalCop() { return totalCop; }
    public double totalUsd() { return totalUsd; }
    public double trmBroadspecCop() { return trmBroadspecCop; }
    public double transferCostCop() { return transferCostCop; }
    public double valorBroadspecCop() { return valorBroadspecCop; }
    public double finesTotal() { return finesTotal; }
    public String finesDisplay() { return finesDisplay; }
    public boolean showFines() { return showFines; }
    public double advancesTotal() { return advancesTotal; }
    public double extrasTotal() { return extrasTotal; }
    public double otherSitesTotalUsd() { return otherSitesTotalUsd; }
    public double usdFromTokens() { return usdFromTokens; }
    public double netUsd() { return netUsd; }
    public double totalUsdPrecalc() { return totalUsdPrecalc; }
    public double usdToSendPlatform() { return usdToSendPlatform; }
    public double btkTrmCop() { return btkTrmCop; }
    public String date() { return date; }
    public double totalTokensAllSites() { return totalTokensAllSites; }
    public double bonusPercentage() { return bonusPercentage; }
    public double bonusAmountUsd() { return bonusAmountUsd; }
    public double bonusAmountCop() { return bonusAmountCop; }
    public double originalPercentage() { return originalPercentage; }
    public double finalPercentage() { return finalPercentage; }
    public double bonusTokensUsed() { return bonusTokensUsed; }
    public double nonBonusTokens() { return nonBonusTokens; }
    public double bonusRatio() { return bonusRatio; }
    public double bonusRate() { return bonusRate; }
    public double lowIncomeReimbursementCop() { return lowIncomeReimbursementCop; }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private double totalCop;
        private double totalUsd;
        private double trmBroadspecCop;
        private double transferCostCop;
        private double valorBroadspecCop;
        private double finesTotal;
        private String finesDisplay = "";
        private boolean showFines = true;
        private double advancesTotal;
        private double extrasTotal;
        private double otherSitesTotalUsd;
        private double usdFromTokens;
        private double netUsd;
        private double totalUsdPrecalc;
        private double usdToSendPlatform;
        private double btkTrmCop;
        private String date = "";
        private double totalTokensAllSites;
        private double bonusPercentage;
        private double bonusAmountUsd;
        private double bonusAmountCop;
        private double originalPercentage;
        private double finalPercentage;
        private double bonusTokensUsed;
        private double nonBonusTokens;
        private double bonusRatio;
        private double bonusRate;
        private double lowIncomeReimbursementCop;

        public Builder totalCop(double v) { totalCop = v; return this; }
        public Builder totalUsd(double v) { totalUsd = v; return this; }
        public Builder trmBroadspecCop(double v) { trmBroadspecCop = v; return this; }
        public Builder transferCostCop(double v) { transferCostCop = v; return this; }
        public Builder valorBroadspecCop(double v) { valorBroadspecCop = v; return this; }
        public Builder finesTotal(double v) { finesTotal = v; return this; }
        public Builder finesDisplay(String v) { finesDisplay = v; return this; }
        public Builder showFines(boolean v) { showFines = v; return this; }
        public Builder advancesTotal(double v) { advancesTotal = v; return this; }
        public Builder extrasTotal(double v) { extrasTotal = v; return this; }
        public Builder otherSitesTotalUsd(double v) { otherSitesTotalUsd = v; return this; }
        public Builder usdFromTokens(double v) { usdFromTokens = v; return this; }
        public Builder netUsd(double v) { netUsd = v; return this; }
        public Builder totalUsdPrecalc(double v) { totalUsdPrecalc = v; return this; }
        public Builder usdToSendPlatform(double v) { usdToSendPlatform = v; return this; }
        public Builder btkTrmCop(double v) { btkTrmCop = v; return this; }
        public Builder date(String v) { date = v; return this; }
        public Builder totalTokensAllSites(double v) { totalTokensAllSites = v; return this; }
        public Builder bonusPercentage(double v) { bonusPercentage = v; return this; }
        public Builder bonusAmountUsd(double v) { bonusAmountUsd = v; return this; }
        public Builder bonusAmountCop(double v) { bonusAmountCop = v; return this; }
        public Builder originalPercentage(double v) { originalPercentage = v; return this; }
        public Builder finalPercentage(double v) { finalPercentage = v; return this; }
        public Builder bonusTokensUsed(double v) { bonusTokensUsed = v; return this; }
        public Builder nonBonusTokens(double v) { nonBonusTokens = v; return this; }
        public Builder bonusRatio(double v) { bonusRatio = v; return this; }
        public Builder bonusRate(double v) { bonusRate = v; return this; }
        public Builder lowIncomeReimbursementCop(double v) { lowIncomeReimbursementCop = v; return this; }

        public CalculationResult build() {
            return new CalculationResult(this);
        }
    }
}
