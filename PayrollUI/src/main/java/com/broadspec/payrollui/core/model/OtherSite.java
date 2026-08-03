package com.broadspec.payrollui.core.model;

public record OtherSite(String siteType, double amount) {

    public double getUsdEquivalent(double tokenToUsdRate) {
        return "USD".equalsIgnoreCase(siteType)
            ? amount
            : amount / tokenToUsdRate;
    }

    public double getTksEquivalent(double tokenToUsdRate) {
        return "USD".equalsIgnoreCase(siteType)
            ? amount * tokenToUsdRate
            : amount;
    }
}
