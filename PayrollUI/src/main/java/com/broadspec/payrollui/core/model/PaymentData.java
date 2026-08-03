package com.broadspec.payrollui.core.model;

import java.util.List;

public record PaymentData(
    String modelId,
    String modelName,
    double trmOfficialCop,
    double btkTrmCop,
    int tokens,
    double percentage,
    double previousFortnightUsd,
    List<OtherSite> otherSites,
    List<Advance> advances,
    List<Advance> extras,
    int finesCount,
    double customFineCop,
    boolean overrideHighTokensTrm,
    boolean disableBonus,
    double bonusTokens,
    boolean belowBtkThreshold
) {
    public PaymentData {
        if (otherSites == null) otherSites = List.of();
        if (advances == null) advances = List.of();
        if (extras == null) extras = List.of();
    }

    public PaymentData(
            String modelId, String modelName,
            double trmOfficialCop, double btkTrmCop,
            int tokens, double percentage,
            double previousFortnightUsd,
            List<OtherSite> otherSites, List<Advance> advances, List<Advance> extras,
            int finesCount, double customFineCop,
            boolean overrideHighTokensTrm, boolean disableBonus) {
        this(modelId, modelName, trmOfficialCop, btkTrmCop, tokens, percentage,
             previousFortnightUsd, otherSites, advances, extras,
             finesCount, customFineCop, overrideHighTokensTrm, disableBonus, 0.0, false);
    }
}
