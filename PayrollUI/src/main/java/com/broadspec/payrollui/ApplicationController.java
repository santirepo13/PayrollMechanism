package com.broadspec.payrollui;

import com.broadspec.payrollui.core.exception.ConfigurationException;
import com.broadspec.payrollui.core.exception.VaultException;
import com.broadspec.payrollui.core.model.CalculationResult;
import com.broadspec.payrollui.core.model.PaymentData;
import com.broadspec.payrollui.core.service.PaymentCalculatorService;
import com.broadspec.payrollui.storage.FileOperations;
import com.broadspec.payrollui.storage.VaultRepository;
import com.broadspec.payrollui.util.PdfProtocols;
import com.broadspec.payrollui.util.Validators;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.yaml.snakeyaml.Yaml;

import java.io.InputStream;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class ApplicationController {

    private static final Logger log = LoggerFactory.getLogger(ApplicationController.class);

    private final Map<String, Object> config;
    private final PaymentCalculatorService calculator;
    private final FileOperations fileOperations;
    private VaultRepository vaultRepository;

    public ApplicationController() {
        this.config = loadConfiguration();

        this.calculator = new PaymentCalculatorService(config);
        this.fileOperations = new FileOperations(config);

        try {
            this.vaultRepository = new VaultRepository(config);
        } catch (ConfigurationException | VaultException e) {
            log.warn("Vault features disabled: {}", e.getMessage());
            this.vaultRepository = null;
        }
    }

    private Map<String, Object> loadConfiguration() {
        InputStream is = getClass().getClassLoader()
            .getResourceAsStream("application.yaml");
        if (is == null) {
            throw new ConfigurationException("Configuration file application.yaml not found");
        }
        Yaml yaml = new Yaml();
        return yaml.load(is);
    }

    public Map<String, Object> getConfig() { return config; }

    public PaymentCalculatorService getCalculator() { return calculator; }

    public FileOperations getFileOperations() { return fileOperations; }

    public VaultRepository getVaultRepository() { return vaultRepository; }

    public boolean isVaultAvailable() { return vaultRepository != null; }

    public CalculationResult calculatePayment(Map<String, Object> formData) {
        PaymentData data = mapToPaymentData(formData);
        List<String> errors = Validators.validatePaymentData(data);
        if (!errors.isEmpty()) {
            throw new com.broadspec.payrollui.core.exception.ValidationException(
                "Validation failed: " + String.join("; ", errors));
        }
        return calculator.calculate(data);
    }

    public String saveReceipt(Map<String, Object> inputData, CalculationResult result) {
        if (vaultRepository == null) {
            throw new VaultException("Vault not available");
        }
        try {
            String filename = PdfProtocols.generateFilename(inputData, result);

            var gen = new com.broadspec.payrollui.core.service.ReceiptGeneratorService();
            byte[] pdfBytes = gen.generatePdfBytes(inputData, result);

            Map<String, String> metadata = new LinkedHashMap<>();
            metadata.put("model_id", String.valueOf(inputData.getOrDefault("model_id", "")));
            metadata.put("model_name", String.valueOf(inputData.getOrDefault("model_name", "")));
            metadata.put("tokens", String.valueOf(inputData.getOrDefault("tokens", "")));
            metadata.put("date", result.date() != null ? result.date() : LocalDate.now().toString());

            var entry = vaultRepository.addBytes(pdfBytes, filename, metadata);
            return entry.vaultFilename();
        } catch (Exception e) {
            throw new com.broadspec.payrollui.core.exception.ReceiptGenerationException(
                "Failed to save receipt: " + e.getMessage(), e);
        }
    }

    public void generateReceiptPdf(Map<String, Object> inputData, CalculationResult result,
                                    Path pdfPath) {
        var gen = new com.broadspec.payrollui.core.service.ReceiptGeneratorService();
        gen.generatePdfToPath(inputData, result, pdfPath);
    }

    public List<Map<String, String>> getVaultEntries() {
        if (vaultRepository == null) return List.of();
        try {
            return vaultRepository.getAllEntries();
        } catch (Exception e) {
            log.error("Error getting vault entries: {}", e.getMessage());
            return List.of();
        }
    }

    public Path exportFromVault(String vaultFilename) {
        if (vaultRepository == null) throw new VaultException("Vault not available");
        try {
            byte[] fileBytes = vaultRepository.retrieveFile(vaultFilename);
            Path receiptsDir = fileOperations.ensureReceiptsDirectory();
            Path exportPath = fileOperations.getUniqueFilepath(receiptsDir, vaultFilename);
            fileOperations.saveFile(exportPath, fileBytes);
            return exportPath;
        } catch (Exception e) {
            throw new VaultException("Failed to export from vault: " + e.getMessage(), e);
        }
    }

    public int deleteFromVault(List<String> vaultFilenames) {
        if (vaultRepository == null) throw new VaultException("Vault not available");
        return vaultRepository.deleteFiles(vaultFilenames);
    }

    public int[] importToVault(List<Path> filePaths) {
        if (vaultRepository == null) throw new VaultException("Vault not available");
        int success = 0;
        int failure = 0;
        for (Path fp : filePaths) {
            try {
                Map<String, String> meta = new LinkedHashMap<>();
                meta.put("model_id", "");
                meta.put("model_name", "");
                meta.put("tokens", "");
                meta.put("date", LocalDate.now().toString());
                vaultRepository.addFile(fp, meta);
                success++;
            } catch (Exception e) {
                log.warn("Failed to import {}: {}", fp, e.getMessage());
                failure++;
            }
        }
        return new int[]{success, failure};
    }

    public Map<String, Object> getVaultStats() {
        if (vaultRepository == null) return Map.of("count", 0, "size", 0L);
        try {
            int count = vaultRepository.getAllEntries().size();
            long size = vaultRepository.getVaultSize();
            return Map.of("count", count, "size", size);
        } catch (Exception e) {
            return Map.of("count", 0, "size", 0L);
        }
    }

    @SuppressWarnings("unchecked")
    private PaymentData mapToPaymentData(Map<String, Object> form) {
        List<Map<String, Object>> sites =
            (List<Map<String, Object>>) form.getOrDefault("other_sites", List.of());
        List<com.broadspec.payrollui.core.model.OtherSite> otherSites = sites.stream()
            .map(s -> new com.broadspec.payrollui.core.model.OtherSite(
                String.valueOf(s.getOrDefault("site_type", "USD")),
                toDouble(s.get("amount"), 0)))
            .toList();

        List<Map<String, Object>> advs =
            (List<Map<String, Object>>) form.getOrDefault("advances", List.of());
        List<com.broadspec.payrollui.core.model.Advance> advances = advs.stream()
            .map(a -> new com.broadspec.payrollui.core.model.Advance(
                String.valueOf(a.getOrDefault("date", "")),
                toDouble(a.get("amount"), 0)))
            .toList();

        List<Map<String, Object>> extra =
            (List<Map<String, Object>>) form.getOrDefault("extras", List.of());
        List<com.broadspec.payrollui.core.model.Advance> extras = extra.stream()
            .map(a -> new com.broadspec.payrollui.core.model.Advance(
                String.valueOf(a.getOrDefault("date", "")),
                toDouble(a.get("amount"), 0)))
            .toList();

        return new PaymentData(
            String.valueOf(form.getOrDefault("model_id", "")),
            String.valueOf(form.getOrDefault("model_name", "")),
            toDouble(form.get("trm_official_cop"), 0),
            toDouble(form.get("btk_trm_cop"), 0),
            toInt(form.get("tokens"), 0),
            toDouble(form.get("percentage"), 0),
            toDouble(form.get("previous_fortnight_usd"), 0),
            otherSites, advances, extras,
            toInt(form.get("fines_count"), 0),
            toDouble(form.get("custom_fine_cop"), 0),
            toBoolean(form.get("override_high_tokens_trm")),
            toBoolean(form.get("disable_bonus")),
            toDouble(form.get("bonus_tokens"), 0),
            toBoolean(form.get("below_btk_threshold"))
        );
    }

    public Map<String, Object> paymentDataToMap(PaymentData data) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("model_id", data.modelId());
        map.put("model_name", data.modelName());
        map.put("trm_official_cop", data.trmOfficialCop());
        map.put("btk_trm_cop", data.btkTrmCop());
        map.put("tokens", data.tokens());
        map.put("percentage", data.percentage());
        map.put("previous_fortnight_usd", data.previousFortnightUsd());
        map.put("fines_count", data.finesCount());
        map.put("custom_fine_cop", data.customFineCop());
        map.put("override_high_tokens_trm", data.overrideHighTokensTrm());
        map.put("disable_bonus", data.disableBonus());
        map.put("bonus_tokens", data.bonusTokens());
        map.put("below_btk_threshold", data.belowBtkThreshold());
        return map;
    }

    public Map<String, Object> resultToMap(CalculationResult r) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("total_cop", r.totalCop());
        map.put("total_usd", r.totalUsd());
        map.put("trm_broadspec_cop", r.trmBroadspecCop());
        map.put("transfer_cost_cop", r.transferCostCop());
        map.put("valor_broadspec_cop", r.valorBroadspecCop());
        map.put("fines_total", r.finesTotal());
        map.put("fines_display", r.finesDisplay());
        map.put("show_fines", r.showFines());
        map.put("advances_total", r.advancesTotal());
        map.put("extras_total", r.extrasTotal());
        map.put("other_sites_total_usd", r.otherSitesTotalUsd());
        map.put("usd_from_tokens", r.usdFromTokens());
        map.put("net_usd", r.netUsd());
        map.put("total_usd_precalc", r.totalUsdPrecalc());
        map.put("usd_to_send_platform", r.usdToSendPlatform());
        map.put("btk_trm_cop", r.btkTrmCop());
        map.put("date", r.date());
        map.put("total_tokens_all_sites", r.totalTokensAllSites());
        map.put("bonus_percentage", r.bonusPercentage());
        map.put("bonus_amount_usd", r.bonusAmountUsd());
        map.put("bonus_amount_cop", r.bonusAmountCop());
        map.put("original_percentage", r.originalPercentage());
        map.put("final_percentage", r.finalPercentage());
        map.put("bonus_tokens_used", r.bonusTokensUsed());
        map.put("non_bonus_tokens", r.nonBonusTokens());
        map.put("bonus_ratio", r.bonusRatio());
        map.put("bonus_rate", r.bonusRate());
        map.put("low_income_reimbursement_cop", r.lowIncomeReimbursementCop());
        return map;
    }

    private static double toDouble(Object value, double def) {
        if (value instanceof Number n) return n.doubleValue();
        if (value instanceof String s) {
            try { return Double.parseDouble(s); } catch (NumberFormatException ignored) {}
        }
        return def;
    }

    private static int toInt(Object value, int def) {
        if (value instanceof Number n) return n.intValue();
        if (value instanceof String s) {
            try { return Integer.parseInt(s); } catch (NumberFormatException ignored) {}
        }
        return def;
    }

    private static boolean toBoolean(Object value) {
        if (value instanceof Boolean b) return b;
        if (value instanceof String s) return Boolean.parseBoolean(s);
        return false;
    }
}
