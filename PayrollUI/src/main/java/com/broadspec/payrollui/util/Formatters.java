package com.broadspec.payrollui.util;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class Formatters {

    private Formatters() {}

    public static String formatCurrencyCop(double amount) {
        return String.format("$%,.2f COP", amount);
    }

    public static String formatCurrencyCop(double amount, boolean showDecimals) {
        return showDecimals
            ? String.format("$%,.2f COP", amount)
            : String.format("$%,.0f COP", amount);
    }

    public static String formatCurrencyUsd(double amount) {
        return String.format("$%,.2f", amount);
    }

    public static String formatCurrency(String currency, double amount) {
        if ("USD".equalsIgnoreCase(currency)) {
            return formatCurrencyUsd(amount) + " USD";
        }
        return formatCurrencyCop(amount);
    }

    public static String sanitizeFilename(String name) {
        if (name == null || name.isEmpty()) return "unnamed";
        return name.replaceAll("[<>:\"/\\\\|?*\\x00-\\x1F]", "_")
                   .replaceAll("[\\s.]+$", "")
                   .trim();
    }

    public static String humanReadableSize(long bytes) {
        String[] units = {"B", "KB", "MB", "GB", "TB"};
        double size = bytes;
        int unitIndex = 0;
        while (size >= 1024.0 && unitIndex < units.length - 1) {
            size /= 1024.0;
            unitIndex++;
        }
        return unitIndex == 0
            ? String.format("%d %s", (long) size, units[unitIndex])
            : String.format("%.1f %s", size, units[unitIndex]);
    }

    public static Map<String, String> parseFilenameMetadata(String filename) {
        Map<String, String> result = new LinkedHashMap<>();
        result.put("model_id", "");
        result.put("model_name", "");
        result.put("tokens", "");
        result.put("date", "");

        if (filename == null || filename.isEmpty()) return result;

        String base = filename.replaceAll("\\\\", "/");
        int lastSlash = base.lastIndexOf('/');
        if (lastSlash >= 0) base = base.substring(lastSlash + 1);
        base = base.replaceAll("\\.pdf$", "");

        Matcher dateMatcher = Pattern.compile("(\\d{4}-\\d{2}-\\d{2})$").matcher(base);
        if (dateMatcher.find()) {
            result.put("date", dateMatcher.group(1));
            base = base.substring(0, dateMatcher.start()).replaceAll("\\s*-\\s*$", "");
        }

        String[] parts = java.util.Arrays.stream(base.split("\\s*-\\s*"))
            .map(String::trim)
            .filter(s -> !s.isEmpty())
            .toArray(String[]::new);

        if (parts.length >= 1) result.put("model_id", parts[0]);

        int tokenIndex = -1;
        for (int i = parts.length - 1; i > 0; i--) {
            if (Pattern.compile("\\b\\d[\\d,.]*\\s*(TKS)?\\b", Pattern.CASE_INSENSITIVE)
                    .matcher(parts[i]).find()) {
                tokenIndex = i;
                break;
            }
        }

        if (tokenIndex != -1) {
            result.put("tokens", parts[tokenIndex]);
            if (tokenIndex > 1) {
                result.put("model_name", String.join(" - ",
                    java.util.Arrays.copyOfRange(parts, 1, tokenIndex)));
            } else if (parts.length > 1) {
                result.put("model_name", parts[1]);
            }
        } else {
            if (parts.length >= 3) {
                result.put("tokens", parts[parts.length - 1]);
                result.put("model_name", String.join(" - ",
                    java.util.Arrays.copyOfRange(parts, 1, parts.length - 1)));
            } else if (parts.length > 1) {
                result.put("model_name", String.join(" - ",
                    java.util.Arrays.copyOfRange(parts, 1, parts.length)));
            }
        }

        return result;
    }
}
