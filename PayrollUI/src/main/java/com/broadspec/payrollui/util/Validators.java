package com.broadspec.payrollui.util;

import com.broadspec.payrollui.core.model.PaymentData;

import java.util.ArrayList;
import java.util.List;

public final class Validators {

    private Validators() {}

    public static List<String> validatePaymentData(PaymentData data) {
        List<String> errors = new ArrayList<>();

        if (data.modelId() == null || data.modelId().isBlank())
            errors.add("Model ID is required");

        if (data.trmOfficialCop() <= 0)
            errors.add("TRM Official COP must be greater than 0");

        if (data.btkTrmCop() <= 0)
            errors.add("BTK TRM COP must be greater than 0");

        if (data.tokens() < 0)
            errors.add("Tokens cannot be negative");

        double percent = data.percentage() > 1 ? data.percentage() / 100.0 : data.percentage();
        if (percent <= 0 || percent > 1)
            errors.add("Percentage must be between 0 and 1");

        if (data.previousFortnightUsd() < 0)
            errors.add("Previous Fortnight USD cannot be negative");

        if (data.finesCount() < 0)
            errors.add("Fines count cannot be negative");

        if (data.customFineCop() < 0)
            errors.add("Custom fine amount cannot be negative");

        for (int i = 0; i < data.advances().size(); i++) {
            if (data.advances().get(i).amount() < 0)
                errors.add("Advance " + (i + 1) + " amount cannot be negative");
        }

        for (int i = 0; i < data.extras().size(); i++) {
            if (data.extras().get(i).amount() < 0)
                errors.add("Extra " + (i + 1) + " amount cannot be negative");
        }

        for (int i = 0; i < data.otherSites().size(); i++) {
            var site = data.otherSites().get(i);
            if (site.amount() < 0)
                errors.add("Other Site " + (i + 1) + " amount cannot be negative");
            if (!List.of("USD", "TKS").contains(site.siteType().toUpperCase()))
                errors.add("Other Site " + (i + 1) + " type must be USD or TKS");
        }

        return errors;
    }

    public static String sanitizeNumericInput(String value) {
        return value.replace(",", "").trim();
    }
}
