package com.broadspec.payrollui.core.service;

import com.broadspec.payrollui.core.exception.ReceiptGenerationException;
import com.broadspec.payrollui.core.model.CalculationResult;
import com.broadspec.payrollui.util.Formatters;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.apache.pdfbox.pdmodel.font.Standard14Fonts;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

public class ReceiptGeneratorService {

    private static final float LETTER_HEIGHT = PDRectangle.LETTER.getHeight();

    public byte[] generatePdfBytes(Map<String, Object> inputData, CalculationResult result) {
        try (PDDocument doc = new PDDocument();
             ByteArrayOutputStream baos = new ByteArrayOutputStream()) {

            addFullReceiptPage(doc, inputData, result);
            addSimpleReceiptPage(doc, inputData, result);

            doc.save(baos);
            return baos.toByteArray();
        } catch (IOException e) {
            throw new ReceiptGenerationException(
                "Failed to generate PDF bytes: " + e.getMessage(), e);
        }
    }

    public void generatePdfToPath(Map<String, Object> inputData, CalculationResult result,
                                   Path pdfPath) {
        try {
            Files.createDirectories(pdfPath.getParent());
            try (PDDocument doc = new PDDocument()) {
                addFullReceiptPage(doc, inputData, result);
                addSimpleReceiptPage(doc, inputData, result);
                doc.save(pdfPath.toFile());
            }
        } catch (IOException e) {
            throw new ReceiptGenerationException(
                "Failed to generate PDF: " + e.getMessage(), e);
        }
    }

    private void addFullReceiptPage(PDDocument doc, Map<String, Object> data,
                                     CalculationResult result) throws IOException {
        PDPage page = new PDPage(PDRectangle.LETTER);
        doc.addPage(page);

        try (PDPageContentStream cs = new PDPageContentStream(doc, page)) {
            float y = LETTER_HEIGHT - 50;
            cs.beginText();
            cs.setFont(new PDType1Font(Standard14Fonts.FontName.COURIER_BOLD), 16);
            cs.newLineAtOffset(50, y);
            cs.showText("BROADSPEC PAYMENT RECEIPTS");
            cs.endText();

            y -= 50;
            String[] lines = generateFullReceiptLines(data, result);
            cs.setFont(new PDType1Font(Standard14Fonts.FontName.COURIER), 9);

            for (String line : lines) {
                if (y < 50) {
                    cs.close();
                    page = new PDPage(PDRectangle.LETTER);
                    doc.addPage(page);
                    cs.setFont(new PDType1Font(Standard14Fonts.FontName.COURIER), 9);
                    y = LETTER_HEIGHT - 50;
                }
                cs.beginText();
                cs.newLineAtOffset(50, y);
                cs.showText(line.length() > 80 ? line.substring(0, 80) : line);
                cs.endText();
                y -= 12;
            }
        }
    }

    private void addSimpleReceiptPage(PDDocument doc, Map<String, Object> data,
                                       CalculationResult result) throws IOException {
        PDPage page = new PDPage(PDRectangle.LETTER);
        doc.addPage(page);

        try (PDPageContentStream cs = new PDPageContentStream(doc, page)) {
            float y = LETTER_HEIGHT - 50;
            cs.beginText();
            cs.setFont(new PDType1Font(Standard14Fonts.FontName.COURIER_BOLD), 14);
            cs.newLineAtOffset(50, y);
            cs.showText("MODEL RECEIPT");
            cs.endText();

            y -= 50;
            String[] lines = generateSimpleReceiptLines(data, result);
            cs.setFont(new PDType1Font(Standard14Fonts.FontName.COURIER), 10);

            for (String line : lines) {
                if (y < 50) break;
                cs.beginText();
                cs.newLineAtOffset(50, y);
                cs.showText(line.length() > 80 ? line.substring(0, 80) : line);
                cs.endText();
                y -= 14;
            }
        }
    }

    @SuppressWarnings("unchecked")
    private String[] generateFullReceiptLines(Map<String, Object> data,
                                               CalculationResult result) {
        String eq = "=".repeat(50);
        String date = result.date() != null && !result.date().isEmpty()
            ? result.date() : java.time.LocalDate.now().toString();

        java.util.List<String> lines = new java.util.ArrayList<>();
        lines.add(eq);
        lines.add("            PAYMENT RECEIPT");
        lines.add("              BROADSPEC");
        lines.add(eq);
        lines.add("Model ID: " + data.getOrDefault("model_id", ""));
        lines.add("Model: " + data.getOrDefault("model_name", ""));
        lines.add("Date: " + date);
        lines.add(eq);
        lines.add("");
        lines.add("INPUT VALUES:");
        lines.add("  TRM Official: " + Formatters.formatCurrencyCop(
            toDouble(data.get("trm_official_cop"))));
        lines.add("  TRM BroadSpec: " + Formatters.formatCurrencyCop(
            result.trmBroadspecCop()));
        lines.add("  Tokens (TKS): " + String.format("%,d", (int) toDouble(data.get("tokens"))));
        lines.add("  Percentage: " + String.format("%.0f%%",
            toDouble(data.get("percentage")) * 100));
        lines.add("  Other Sites (USD equivalent):");

        List<Map<String, Object>> sites = (List<Map<String, Object>>)
            data.getOrDefault("other_sites", List.of());
        if (sites.isEmpty() || sites.stream().noneMatch(s -> toDouble(s.get("amount")) > 0)) {
            lines.add("None");
        } else {
            for (int i = 0; i < sites.size(); i++) {
                var s = sites.get(i);
                double amt = toDouble(s.get("amount"));
                if (amt <= 0) continue;
                if ("USD".equals(s.get("site_type"))) {
                    lines.add("Site " + (i + 2) + ": " +
                        Formatters.formatCurrencyUsd(amt) + " USD");
                } else {
                    lines.add("Site " + (i + 2) + ": " + String.format("%,d TKS => %s USD",
                        (int) amt, Formatters.formatCurrencyUsd(amt / 20.0)));
                }
            }
        }

        lines.add("  Previous Fortnight USD: " + Formatters.formatCurrencyUsd(
            toDouble(data.get("previous_fortnight_usd"))));
        lines.add("");
        lines.add("ADVANCES:");

        List<Map<String, Object>> advances = (List<Map<String, Object>>)
            data.getOrDefault("advances", List.of());
        if (advances.isEmpty() || advances.stream().noneMatch(a -> toDouble(a.get("amount")) > 0)) {
            lines.add("None");
        } else {
            for (var a : advances) {
                double amt = toDouble(a.get("amount"));
                if (amt <= 0) continue;
                lines.add(a.get("date") + ": " + Formatters.formatCurrencyCop(amt));
            }
        }
        lines.add("");

        lines.add("  Total: " + Formatters.formatCurrencyCop(result.advancesTotal()));
        lines.add("");
        lines.add("FINES:");
        if (result.showFines()) {
            lines.add("  " + result.finesDisplay());
        } else {
            lines.add("  Fines: Disabled (Home Worker)");
        }
        lines.add("");
        lines.add("CALCULATED VALUES:");
        lines.add("  USD from Tokens: " + Formatters.formatCurrencyUsd(result.usdFromTokens()));
        lines.add("  Net Amount USD: " + Formatters.formatCurrencyUsd(result.netUsd()));
        lines.add("  Total USD (Pre-calc): " + Formatters.formatCurrencyUsd(result.totalUsdPrecalc()));
        lines.add("  Total USD in COP: " + Formatters.formatCurrencyCop(
            result.totalUsdPrecalc() * result.trmBroadspecCop()));
        lines.add("  Transfer Cost: " + Formatters.formatCurrencyCop(result.transferCostCop()));
        lines.add("");
        lines.add("BONUS INFORMATION:");
        lines.add("  Total Tokens (All Sites): " +
            String.format("%,.0f", result.totalTokensAllSites()) + " TKS");
        lines.add("  Bonus Tokens: " +
            String.format("%,.0f", result.bonusTokensUsed()) + " TKS");
        lines.add("  Non-Bonus Tokens: " +
            String.format("%,.0f", result.nonBonusTokens()) + " TKS");
        lines.add("  Bonus Rate: " +
            String.format("%.1f%%", result.bonusRate() * 100) + " (" +
            String.format("%.1f%%", result.originalPercentage() * 100) + " + " +
            String.format("%.1f%%", result.bonusPercentage() * 100) + ")");
        lines.add("  Base Rate: " +
            String.format("%.1f%%", result.originalPercentage() * 100));
        lines.add("  Bonus Amount: " +
            Formatters.formatCurrencyUsd(result.bonusAmountUsd()) + " USD (" +
            Formatters.formatCurrencyCop(result.bonusAmountCop()) + ")");
        lines.add("");
        lines.add("FINAL CALCULATION:");
        lines.add("  BroadSpec Value: " + Formatters.formatCurrencyCop(result.valorBroadspecCop()));
        lines.add("  Less Advances: " + Formatters.formatCurrencyCop(result.advancesTotal()));
        lines.add("  Less Fines: " + Formatters.formatCurrencyCop(result.finesTotal()));

        if (result.lowIncomeReimbursementCop() > 0) {
            lines.add("  Low Income Reimbursement: " +
                Formatters.formatCurrencyCop(result.lowIncomeReimbursementCop()));
        }

        lines.add("");
        lines.add("  TOTAL PAYMENT: " + Formatters.formatCurrencyCop(result.totalCop()));
        lines.add("  TOTAL PAYMENT: " + Formatters.formatCurrencyUsd(result.totalUsd()) + " USD");
        lines.add("");
        lines.add(eq);
        lines.add("     Payment calculation completed");
        lines.add(eq);

        return lines.toArray(new String[0]);
    }

    @SuppressWarnings("unchecked")
    private String[] generateSimpleReceiptLines(Map<String, Object> data,
                                                 CalculationResult result) {
        String eq = "=".repeat(40);
        java.util.List<String> lines = new java.util.ArrayList<>();

        lines.add("");
        lines.add("");
        lines.add("        BROADSPEC");
        lines.add("      Payment Summary");
        lines.add("");
        lines.add("");
        lines.add(eq);
        lines.add("");
        lines.add("Date: " + (result.date() != null ? result.date() : ""));
        lines.add("");
        lines.add("ID: " + data.getOrDefault("model_id", ""));
        lines.add("");
        lines.add("Model: " + data.getOrDefault("model_name", ""));
        lines.add("");
        lines.add("TRM Official: " + Formatters.formatCurrencyCop(
            toDouble(data.get("trm_official_cop"))));
        lines.add("");
        lines.add("TRM BroadSpec: " + Formatters.formatCurrencyCop(
            result.trmBroadspecCop()));
        lines.add("");
        lines.add("Tokens: " + String.format("%,d", (int) toDouble(data.get("tokens"))));
        lines.add("");
        lines.add("Other Sites:");

        List<Map<String, Object>> sites = (List<Map<String, Object>>)
            data.getOrDefault("other_sites", List.of());
        if (sites.isEmpty() || sites.stream().noneMatch(s -> toDouble(s.get("amount")) > 0)) {
            lines.add("  None");
        } else {
            for (int i = 0; i < sites.size(); i++) {
                var s = sites.get(i);
                double amt = toDouble(s.get("amount"));
                if (amt <= 0) continue;
                if ("USD".equals(s.get("site_type"))) {
                    lines.add("  Site " + (i + 2) + ": " +
                        Formatters.formatCurrencyUsd(amt));
                } else {
                    lines.add("  Site " + (i + 2) + ": " +
                        String.format("%,d TKS", (int) amt));
                }
            }
        }
        lines.add("");
        double bonusPct = result.bonusPercentage();
        double bonusUsed = result.bonusTokensUsed();
        double totalAll = result.totalTokensAllSites();

        if (bonusPct > 0) {
            if (bonusUsed > 0 && bonusUsed < totalAll) {
                lines.add("Bonus Rate: " +
                    String.format("%.1f%%", result.bonusRate() * 100) +
                    " (" + String.format("%,.0f", bonusUsed) + " TKS)");
                lines.add("");
                lines.add("Base Rate: " +
                    String.format("%.1f%%", result.originalPercentage() * 100) +
                    " (" + String.format("%,.0f", result.nonBonusTokens()) + " TKS)");
                lines.add("");
                lines.add("Bonus: +" + String.format("%.1f%%", bonusPct * 100));
            } else {
                lines.add("Percentage: " +
                    String.format("%.1f%%", result.bonusRate() * 100));
                lines.add("");
                lines.add("Bonus: +" + String.format("%.1f%%", bonusPct * 100));
            }
            lines.add("");
            lines.add("Bonus Amount: " +
                Formatters.formatCurrencyCop(result.bonusAmountCop()));
            lines.add("");
        } else {
            lines.add("Percentage: " +
                String.format("%.1f%%", result.originalPercentage() * 100));
            lines.add("");
        }
        lines.add("Advances:");

        List<Map<String, Object>> advances = (List<Map<String, Object>>)
            data.getOrDefault("advances", List.of());
        if (advances.isEmpty() || advances.stream().noneMatch(a -> toDouble(a.get("amount")) > 0)) {
            lines.add("  None");
        } else {
            for (var a : advances) {
                double amt = toDouble(a.get("amount"));
                if (amt <= 0) continue;
                lines.add("  " + a.get("date") + ": " +
                    Formatters.formatCurrencyCop(amt, false));
            }
        }
        lines.add("");

        if (result.showFines()) {
            lines.add("Fines: " + Formatters.formatCurrencyCop(result.finesTotal(), false));
            lines.add("");
        }

        if (result.lowIncomeReimbursementCop() > 0) {
            lines.add("Low Income Reimbursement: " +
                Formatters.formatCurrencyCop(result.lowIncomeReimbursementCop(), false));
            lines.add("");
        }

        lines.add("Total Payment:");
        lines.add(Formatters.formatCurrencyCop(result.totalCop()));
        lines.add("");
        lines.add(eq);

        return lines.toArray(new String[0]);
    }

    private static double toDouble(Object value) {
        return toDouble(value, 0.0);
    }

    private static double toDouble(Object value, double def) {
        if (value instanceof Number n) return n.doubleValue();
        if (value instanceof String s && !s.isBlank()) {
            try { return Double.parseDouble(s.replace(",", "")); }
            catch (NumberFormatException ignored) {}
        }
        return def;
    }
}
