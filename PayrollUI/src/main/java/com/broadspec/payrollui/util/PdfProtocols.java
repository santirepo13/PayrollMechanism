package com.broadspec.payrollui.util;

import com.broadspec.payrollui.core.model.CalculationResult;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

public final class PdfProtocols {

    private PdfProtocols() {}

    public static String generateFilename(
            Map<String, Object> data, CalculationResult result) {

        String dateStr = result != null && result.date() != null && !result.date().isEmpty()
            ? result.date()
            : LocalDate.now().toString();

        String modelId = sanitizeFilename(String.valueOf(data.getOrDefault("model_id", "")).trim());
        String modelName = sanitizeFilename(String.valueOf(data.getOrDefault("model_name", "")).trim());

        int explicitTokens = 0;
        try {
            explicitTokens = Integer.parseInt(String.valueOf(data.getOrDefault("tokens", "0")).trim());
        } catch (NumberFormatException ignored) {}

        int tokensFromSites = 0;
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> sites =
            (List<Map<String, Object>>) data.getOrDefault("other_sites", List.of());
        for (var site : sites) {
            try {
                double amt = Double.parseDouble(String.valueOf(site.getOrDefault("amount", 0)));
                String type = String.valueOf(site.getOrDefault("site_type", "USD")).toUpperCase();
                if ("USD".equals(type)) {
                    tokensFromSites += (int) Math.round(amt * 20);
                } else {
                    tokensFromSites += (int) Math.round(amt);
                }
            } catch (NumberFormatException ignored) {}
        }

        int tokensTotal = explicitTokens + tokensFromSites;

        String usdAmount = "";
        String copAmount = "";
        if (result != null) {
            if (result.usdToSendPlatform() > 0) {
                usdAmount = String.format("%.3f USD", result.usdToSendPlatform());
            } else if (result.totalUsd() > 0) {
                usdAmount = String.format("%.3f USD", result.totalUsd());
            }
            if (result.totalCop() > 0) {
                copAmount = String.format("%,.0f COP", result.totalCop())
                    .replace(",", ".");
            }
        }

        return String.format("%s - %s - %d TKS - %s - %s - %s.pdf",
            modelId, modelName, tokensTotal, usdAmount, copAmount, dateStr);
    }

    private static String sanitizeFilename(String name) {
        if (name == null || name.isEmpty()) return "unnamed";
        return name.replaceAll("[<>:\"/\\\\|?*\\x00-\\x1F]", "_")
                   .replaceAll("[\\s.]+$", "")
                   .replaceAll("\\s+", " ")
                   .trim();
    }
}
