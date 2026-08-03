package com.broadspec.payrollui.ui;

import com.broadspec.payrollui.ApplicationController;

import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class MainTabView {

    private final ApplicationController controller;
    private final MainWindow mainWindow;
    private final VBox root;

    private final TextField modelIdField;
    private final TextField modelNameField;
    private final TextField trmOfficialField;
    private final TextField btkTrmField;
    private final CheckBox overrideTrmCheck;
    private final CheckBox disableBonusCheck;
    private final CheckBox belowBtkThresholdCheck;
    private final TextField tokensField;
    private final ComboBox<String> percentageCombo;
    private final TextField previousFortnightField;
    private final TextField finesCountField;
    private final TextField customFineField;
    private final Label totalTokensLabel;
    private final TextField bonusTokensField;

    private final VBox otherSitesContainer;
    private final List<OtherSiteRow> otherSiteRows = new ArrayList<>();
    private final VBox advancesContainer;
    private final List<AdvanceRow> advanceRows = new ArrayList<>();
    private final VBox extrasContainer;
    private final List<AdvanceRow> extraRows = new ArrayList<>();

    private final TextArea fullReceiptText;
    private final TextArea modelReceiptText;

    private final Label finesLabel;
    private final Label fineCountLabel;
    private final Label customFineLabel;

    private Map<String, Object> currentInputData;
    private Map<String, Object> currentResultData;

    public MainTabView(ApplicationController controller, MainWindow mainWindow) {
        this.controller = controller;
        this.mainWindow = mainWindow;

        this.modelIdField = new TextField();
        this.modelNameField = new TextField();
        this.trmOfficialField = new TextField();
        this.btkTrmField = new TextField();
        this.overrideTrmCheck = new CheckBox("Always apply -300 TRM (ignore 3000+ TKS rule)");
        this.disableBonusCheck = new CheckBox("Disable All Bonuses (ignore token bonus thresholds)");
        this.belowBtkThresholdCheck = new CheckBox("Payment Below BTK Threshold (reimburse payment fee)");
        this.tokensField = new TextField();
        this.percentageCombo = new ComboBox<>();
        percentageCombo.getItems().addAll("60%", "70%", "75%");
        percentageCombo.setValue("70%");
        this.previousFortnightField = new TextField("0");
        this.finesCountField = new TextField("0");
        this.customFineField = new TextField();
        this.totalTokensLabel = new Label("0 TKS");
        totalTokensLabel.setFont(Font.font("Arial", 12));
        this.bonusTokensField = new TextField("0");

        this.otherSitesContainer = new VBox(2);
        this.advancesContainer = new VBox(2);
        this.extrasContainer = new VBox(2);

        this.fullReceiptText = new TextArea();
        fullReceiptText.setEditable(false);
        fullReceiptText.setWrapText(true);
        fullReceiptText.setFont(Font.font("Courier New", 11));

        this.modelReceiptText = new TextArea();
        modelReceiptText.setEditable(false);
        modelReceiptText.setWrapText(true);
        modelReceiptText.setFont(Font.font("Courier New", 11));

        this.finesLabel = new Label("Fines (Studio only):");
        finesLabel.setFont(Font.font("Arial", FontWeight.BOLD, 12));
        this.fineCountLabel = new Label("Number of Fines (30k each):");
        this.customFineLabel = new Label("OR Custom Fine Amount (COP):");

        root = buildLayout();
    }

    public VBox getRoot() { return root; }

    private VBox buildLayout() {
        VBox mainBox = new VBox(10);
        mainBox.setPadding(new Insets(10));

        Label title = new Label("BROADSPEC PAYMENT CALCULATOR");
        title.setFont(Font.font("Arial", FontWeight.BOLD, 16));
        title.setPadding(new Insets(0, 0, 10, 0));

        HBox contentRow = new HBox(10);

        ScrollPane inputScroll = new ScrollPane(buildInputPanel());
        inputScroll.setFitToWidth(true);
        inputScroll.setMinWidth(360);

        SplitPane receiptPane = new SplitPane();
        receiptPane.setOrientation(javafx.geometry.Orientation.HORIZONTAL);

        VBox fullReceiptBox = new VBox(5);
        fullReceiptBox.getChildren().add(new Label("Full Receipt"));
        fullReceiptBox.getChildren().add(fullReceiptText);
        VBox.setVgrow(fullReceiptText, Priority.ALWAYS);

        VBox modelReceiptBox = new VBox(5);
        modelReceiptBox.getChildren().add(new Label("Payment Confirmation"));
        modelReceiptBox.getChildren().add(modelReceiptText);

        receiptPane.getItems().addAll(fullReceiptBox, modelReceiptBox);
        receiptPane.setDividerPositions(0.5);

        HBox buttonBar = new HBox(5);
        buttonBar.setPadding(new Insets(10, 0, 0, 0));
        Button calcBtn = new Button("Calculate");
        calcBtn.setOnAction(e -> handleCalculate());
        Button clearBtn = new Button("Clear Fields");
        clearBtn.setOnAction(e -> clearFields());
        Button saveImageBtn = new Button("Save Model Image");
        saveImageBtn.setOnAction(e -> handleSaveModelImage());
        Button savePdfBtn = new Button("Save PDF");
        savePdfBtn.setOnAction(e -> handleSavePdf());
        buttonBar.getChildren().addAll(calcBtn, clearBtn, saveImageBtn, savePdfBtn);

        HBox.setHgrow(inputScroll, Priority.NEVER);
        HBox.setHgrow(receiptPane, Priority.ALWAYS);

        contentRow.getChildren().addAll(inputScroll, receiptPane);

        mainBox.getChildren().addAll(title, contentRow, buttonBar);

        addOtherSiteRow();
        addAdvanceRow();
        addExtraRow();
        updateFinesState();

        return mainBox;
    }

    private VBox buildInputPanel() {
        VBox panel = new VBox(5);
        panel.setPadding(new Insets(5));

        panel.getChildren().addAll(
            label("Model ID #:"), modelIdField,
            label("Model Name:"), modelNameField,
            label("TRM Official $COP (NOT NULL):"), trmOfficialField,
            label("BTK TRM $COP:"), btkTrmField,
            overrideTrmCheck,
            disableBonusCheck,
            belowBtkThresholdCheck,
            label("Tokens (TKS):"), tokensField,
            label("Percentage:"), percentageCombo,
            label("Other Sites (USD or TKS):"), otherSitesContainer,
            new Button("+ Add Other Site") {{ setOnAction(e -> addOtherSiteRow()); }},
            label("Total Tokens (All Sites):"), totalTokensLabel,
            label("Tokens for Bonus (TKS):"), bonusTokensField,
            label("Previous Fortnight USD:"), previousFortnightField,
            label("Advances:"), advancesContainer,
            new Button("+ Add Advance") {{ setOnAction(e -> addAdvanceRow()); }},
            label("Extras:"), extrasContainer,
            new Button("+ Add Extra") {{ setOnAction(e -> addExtraRow()); }},
            finesLabel,
            fineCountLabel, finesCountField,
            customFineLabel, customFineField
        );

        percentageCombo.setOnAction(e -> updateFinesState());
        tokensField.setOnKeyReleased(e -> updateTotalTokensDisplay());

        return panel;
    }

    private Label label(String text) {
        Label l = new Label(text);
        l.setMaxWidth(Double.MAX_VALUE);
        return l;
    }

    void addOtherSiteRow() {
        HBox row = new HBox(5);
        ComboBox<String> typeCombo = new ComboBox<>();
        typeCombo.getItems().addAll("USD", "TKS");
        typeCombo.setValue("USD");
        typeCombo.setPrefWidth(70);
        TextField amountField = new TextField("0");
        Button removeBtn = new Button("X");
        removeBtn.setOnAction(e -> {
            otherSitesContainer.getChildren().remove(row);
            otherSiteRows.removeIf(r -> r.row == row);
            if (otherSiteRows.isEmpty()) addOtherSiteRow();
            updateTotalTokensDisplay();
        });
        row.getChildren().addAll(typeCombo, amountField, removeBtn);
        otherSitesContainer.getChildren().add(row);
        otherSiteRows.add(new OtherSiteRow(typeCombo, amountField, row));

        typeCombo.setOnAction(e -> updateTotalTokensDisplay());
        amountField.setOnKeyReleased(e -> updateTotalTokensDisplay());
    }

    void addAdvanceRow() {
        HBox row = new HBox(5);
        TextField dateField = new TextField(LocalDate.now().toString());
        dateField.setPrefWidth(110);
        TextField amountField = new TextField("0");
        Button removeBtn = new Button("X");
        removeBtn.setOnAction(e -> {
            advancesContainer.getChildren().remove(row);
            advanceRows.removeIf(r -> r.row == row);
            if (advanceRows.isEmpty()) addAdvanceRow();
        });
        row.getChildren().addAll(dateField, amountField, removeBtn);
        advancesContainer.getChildren().add(row);
        advanceRows.add(new AdvanceRow(dateField, amountField, row));
    }

    void addExtraRow() {
        HBox row = new HBox(5);
        TextField dateField = new TextField(LocalDate.now().toString());
        dateField.setPrefWidth(110);
        TextField amountField = new TextField("0");
        Button removeBtn = new Button("X");
        removeBtn.setOnAction(e -> {
            extrasContainer.getChildren().remove(row);
            extraRows.removeIf(r -> r.row == row);
            if (extraRows.isEmpty()) addExtraRow();
        });
        row.getChildren().addAll(dateField, amountField, removeBtn);
        extrasContainer.getChildren().add(row);
        extraRows.add(new AdvanceRow(dateField, amountField, row));
    }

    private void updateFinesState() {
        String perc = percentageCombo.getValue();
        double p = perc != null ? Double.parseDouble(perc.replace("%", "")) / 100.0 : 0.7;
        boolean disable = p > 0.60;
        finesCountField.setDisable(disable);
        customFineField.setDisable(disable);
        if (disable) {
            finesCountField.setText("0");
            customFineField.clear();
            finesLabel.setText("Fines (Disabled - Home Worker)");
        } else {
            finesLabel.setText("Fines (Studio only):");
        }
    }

    private void updateTotalTokensDisplay() {
        double total = computeTotalTokens();
        totalTokensLabel.setText(String.format("%.0f TKS", total));
    }

    private double computeTotalTokens() {
        double main = parseDouble(tokensField.getText(), 0);
        for (var row : otherSiteRows) {
            double amt = parseDouble(row.amountField.getText(), 0);
            if ("USD".equals(row.typeCombo.getValue())) {
                main += amt * 20;
            } else {
                main += amt;
            }
        }
        return main;
    }

    private void handleCalculate() {
        try {
            Map<String, Object> formData = collectFormData();
            var result = controller.calculatePayment(formData);
            currentInputData = formData;
            currentResultData = controller.resultToMap(result);

            String fullReceipt = buildFullReceipt(currentInputData, currentResultData);
            String modelReceipt = buildModelReceipt(currentInputData, currentResultData);

            fullReceiptText.setText(fullReceipt);
            modelReceiptText.setText(modelReceipt);

            int modelLines = modelReceipt.split("\n", -1).length;
            modelReceiptText.setPrefRowCount(modelLines + 1);
            modelReceiptText.setPrefColumnCount(40);
        } catch (Exception e) {
            new Alert(Alert.AlertType.ERROR, e.getMessage()).showAndWait();
        }
    }

    private void handleSavePdf() {
        if (currentInputData == null || currentResultData == null) {
            new Alert(Alert.AlertType.WARNING, "Please calculate first before saving").showAndWait();
            return;
        }
        try {
            var resultObj = buildResultFromMap(currentResultData);
            String vaultFilename = controller.saveReceipt(currentInputData, resultObj);
            mainWindow.getVaultTabView().refreshVault();
            new Alert(Alert.AlertType.INFORMATION,
                "PDF saved to encrypted vault as: " + vaultFilename).showAndWait();
        } catch (Exception e) {
            new Alert(Alert.AlertType.ERROR, "Vault Save Error: " + e.getMessage()).showAndWait();
        }
    }

    private void handleSaveModelImage() {
        if (currentInputData == null || currentResultData == null) {
            new Alert(Alert.AlertType.WARNING, "Please calculate first before saving").showAndWait();
            return;
        }

        String text = modelReceiptText.getText();
        javafx.scene.text.Text textNode = new javafx.scene.text.Text(text);
        textNode.setFont(Font.font("Courier New", 11));

        new javafx.scene.Scene(new javafx.scene.Group(textNode));
        javafx.scene.SnapshotParameters params = new javafx.scene.SnapshotParameters();
        params.setFill(javafx.scene.paint.Color.WHITE);
        javafx.scene.image.WritableImage snapshot = textNode.snapshot(params, null);

        java.io.File imgDir = new java.io.File("img");
        imgDir.mkdirs();

        String baseName = currentInputData != null
            ? String.valueOf(currentInputData.getOrDefault("model_name", "receipt"))
            : "receipt";
        java.io.File outFile = new java.io.File(imgDir, baseName + ".jpg");

        try {
            javax.imageio.ImageIO.write(
                javafx.embed.swing.SwingFXUtils.fromFXImage(snapshot, null),
                "JPEG", outFile);
            new Alert(Alert.AlertType.INFORMATION,
                "Model image saved: " + outFile.getPath()).showAndWait();
        } catch (Exception e) {
            new Alert(Alert.AlertType.ERROR,
                "Failed to save model image: " + e.getMessage()).showAndWait();
        }
    }

    private Map<String, Object> collectFormData() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("model_id", modelIdField.getText().trim());
        data.put("model_name", modelNameField.getText());
        data.put("trm_official_cop", parseDouble(trmOfficialField.getText()));
        data.put("btk_trm_cop", parseDouble(btkTrmField.getText()));
        data.put("tokens", parseInt(tokensField.getText()));
        data.put("percentage", parseDouble(percentageCombo.getValue().replace("%", "")) / 100.0);
        data.put("previous_fortnight_usd", parseDouble(previousFortnightField.getText()));
        data.put("fines_count", parseInt(finesCountField.getText()));
        data.put("custom_fine_cop", parseDouble(customFineField.getText()));
        data.put("override_high_tokens_trm", overrideTrmCheck.isSelected());
        data.put("disable_bonus", disableBonusCheck.isSelected());
        data.put("bonus_tokens", parseDouble(bonusTokensField.getText()));
        data.put("below_btk_threshold", belowBtkThresholdCheck.isSelected());

        List<Map<String, Object>> sites = new ArrayList<>();
        for (var row : otherSiteRows) {
            double amt = parseDouble(row.amountField.getText(), 0);
            if (amt > 0) {
                Map<String, Object> s = new LinkedHashMap<>();
                s.put("site_type", row.typeCombo.getValue());
                s.put("amount", amt);
                sites.add(s);
            }
        }
        data.put("other_sites", sites);

        data.put("advances", collectAdvanceRows(advanceRows));
        data.put("extras", collectAdvanceRows(extraRows));

        return data;
    }

    private List<Map<String, Object>> collectAdvanceRows(List<AdvanceRow> rows) {
        List<Map<String, Object>> list = new ArrayList<>();
        for (var row : rows) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("date", row.dateField.getText());
            item.put("amount", parseDouble(row.amountField.getText()));
            list.add(item);
        }
        return list;
    }

    void clearFields() {
        String savedTrmOfficial = trmOfficialField.getText();
        String savedBtkTrm = btkTrmField.getText();

        modelIdField.clear();
        modelNameField.clear();
        tokensField.clear();
        percentageCombo.setValue("70%");
        previousFortnightField.setText("0");
        finesCountField.setText("0");
        customFineField.clear();
        bonusTokensField.setText("0");
        overrideTrmCheck.setSelected(false);
        disableBonusCheck.setSelected(false);
        belowBtkThresholdCheck.setSelected(false);

        otherSiteRows.clear();
        otherSitesContainer.getChildren().clear();
        addOtherSiteRow();

        advanceRows.clear();
        advancesContainer.getChildren().clear();
        addAdvanceRow();

        extraRows.clear();
        extrasContainer.getChildren().clear();
        addExtraRow();

        fullReceiptText.clear();
        modelReceiptText.clear();

        currentInputData = null;
        currentResultData = null;
        updateFinesState();
        updateTotalTokensDisplay();

        trmOfficialField.setText(savedTrmOfficial);
        btkTrmField.setText(savedBtkTrm);
    }

    private String buildFullReceipt(Map<String, Object> in, Map<String, Object> res) {
        String eq = "=".repeat(50);
        String data = res.getOrDefault("date", LocalDate.now().toString()).toString();

        List<String> lines = new ArrayList<>(List.of(
            eq, "            PAYMENT RECEIPT", "              BROADSPEC", eq,
            "Model ID: " + in.getOrDefault("model_id", ""),
            "Model: " + in.getOrDefault("model_name", ""),
            "Date: " + data, eq, "",
            "INPUT VALUES:",
            "  TRM Official $COP: " + fmt(in, "trm_official_cop", 2),
            "  BTK TRM $COP: " + fmt(in, "btk_trm_cop", 2),
            "  TRM BROADSPEC $COP: " + fmt(res, "trm_broadspec_cop", 2),
            "  Tokens (TKS): " + fmtInt(in, "tokens"),
            "  Percentage: " + pct(in, "percentage"),
            "   Other Sites (USD equivalent):",
            formatOtherSites(in),
            "  Previous Fortnight USD: " + fmt(in, "previous_fortnight_usd", 2),
            "",
            "ADVANCES:", formatAdvances(in),
            "  Total: " + fmt(res, "advances_total", 2),
            "",
            "EXTRAS (Money to Model):", formatExtras(in),
            "  Total: " + fmt(res, "extras_total", 2),
            "",
            "BONUS INFORMATION:",
            "  Total Tokens (All Sites): " + fmtInt0(res, "total_tokens_all_sites") + " TKS",
            "  Bonus Tokens: " + fmtInt0(res, "bonus_tokens_used") + " TKS",
            "  Non-Bonus Tokens: " + fmtInt0(res, "non_bonus_tokens") + " TKS",
            "  Bonus Rate: " + pct1(res, "bonus_rate") + " (" +
                pct1(res, "original_percentage") + " + " +
                pct1(res, "bonus_percentage") + ")",
            "  Base Rate: " + pct1(res, "original_percentage"),
            "  Bonus Amount: " + fmt3(res, "bonus_amount_usd") + " USD (" +
                fmt(res, "bonus_amount_cop", 2) + " COP)",
            "",
            "CALCULATED VALUES:",
            "  USD from Tokens: " + fmt3(res, "usd_from_tokens") + " USD",
            "  Net Amount USD: " + fmt3(res, "net_usd") + " USD",
            "  Total USD (Pre-calc): " + fmt3(res, "total_usd_precalc") + " USD",
            "  Transfer Cost: " + fmt(res, "transfer_cost_cop", 2) + " COP",
            "",
            "FINAL CALCULATION:",
            "  BroadSpec Value: " + fmt(res, "valor_broadspec_cop", 2) + " COP",
            "  Less Advances: " + fmt(res, "advances_total", 2) + " COP",
            "  Plus Extras: " + fmt(res, "extras_total", 2) + " COP",
            "  Less Fines: " + fmt(res, "fines_total", 2) + " COP"
        ));

        double reimbursement = toDouble(res.get("low_income_reimbursement_cop"), 0);
        if (reimbursement > 0) {
            lines.add("  Low Income Reimbursement: " + fmt(res, "low_income_reimbursement_cop", 2) + " COP");
        }

        lines.addAll(List.of(
            "",
            "  TOTAL PAYMENT: " + fmt(res, "total_cop", 2) + " COP",
            "  TOTAL PAYMENT: " + fmt3(res, "total_usd") + " USD",
            "  USD to Send (Platform): " + fmt3(res, "usd_to_send_platform") + " USD",
            "",
            eq,
            "     Payment calculation completed",
            eq
        ));

        return String.join("\n", lines);
    }

    private String buildModelReceipt(Map<String, Object> in, Map<String, Object> res) {
        String sep = "-".repeat(38);
        String data = res.getOrDefault("date", LocalDate.now().toString()).toString();

        List<String> parts = new ArrayList<>(List.of(
            center("BROADSPEC", 38), center("Payment Summary", 38), "",
            sep, "Date: " + data, "", "ID: " + in.getOrDefault("model_id", ""), "",
            "Model: " + in.getOrDefault("model_name", ""), "",
            "TRM Official: " + fmt(in, "trm_official_cop", 2) + " COP",
            "TRM BroadSpec: " + fmt(res, "trm_broadspec_cop", 2) + " COP", "",
            "Tokens: " + fmtInt(in, "tokens")
        ));

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> sites = (List<Map<String, Object>>)
            in.getOrDefault("other_sites", List.of());
        if (sites.stream().anyMatch(s -> parseDouble(s.get("amount"), 0) > 0)) {
            parts.add("");
            parts.add("Other Sites:");
            for (int i = 0; i < sites.size(); i++) {
                var s = sites.get(i);
                double amt = parseDouble(s.get("amount"), 0);
                if (amt <= 0) continue;
                if ("USD".equals(s.get("site_type"))) {
                    parts.add("  Site " + (i + 2) + ": " + String.format("%,.2f", amt) + " USD");
                } else {
                    parts.add("  Site " + (i + 2) + ": " + (int)amt + " TKS");
                }
            }
        }

        double bonusPct = toDouble(res.get("bonus_percentage"), 0);
        double bonusUsed = toDouble(res.get("bonus_tokens_used"), 0);
        double totalAll = toDouble(res.get("total_tokens_all_sites"), 0);

        if (bonusPct > 0) {
            if (bonusUsed > 0 && bonusUsed < totalAll) {
                parts.add("");
                parts.add("Bonus Rate: " + pct1(res, "bonus_rate")
                    + " (" + fmtInt0(res, "bonus_tokens_used") + " TKS)");
                parts.add("Base Rate: " + pct1(res, "original_percentage")
                    + " (" + fmtInt0(res, "non_bonus_tokens") + " TKS)");
                parts.add("");
                parts.add("Bonus: +" + pct1(res, "bonus_percentage"));
            } else {
                parts.add("");
                parts.add("Percentage: " + pct1(res, "bonus_rate"));
                parts.add("");
                parts.add("Bonus: +" + pct1(res, "bonus_percentage"));
            }
            parts.add("");
            parts.add("Bonus Amount: " + fmt(res, "bonus_amount_cop", 2) + " COP");
        } else {
            parts.add("");
            parts.add("Percentage: " + pct1(res, "original_percentage"));
        }

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> advances = (List<Map<String, Object>>)
            in.getOrDefault("advances", List.of());
        if (advances.stream().anyMatch(a -> parseDouble(a.get("amount"), 0) > 0)) {
            parts.add("");
            parts.add("Advances:");
            for (var a : advances) {
                double amt = parseDouble(a.get("amount"), 0);
                if (amt > 0) parts.add("  " + a.get("date") + ": " +
                    String.format("%,.2f COP", amt));
            }
        }

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> extras = (List<Map<String, Object>>)
            in.getOrDefault("extras", List.of());
        if (extras.stream().anyMatch(a -> parseDouble(a.get("amount"), 0) > 0)) {
            parts.add("");
            parts.add("Extras:");
            for (var a : extras) {
                double amt = parseDouble(a.get("amount"), 0);
                if (amt > 0) parts.add("  " + a.get("date") + ": " +
                    String.format("%,.2f COP", amt));
            }
        }

        if (Boolean.TRUE.equals(res.get("show_fines"))) {
            parts.add("");
            parts.add("Fines: " + fmt(res, "fines_total", 2) + " COP");
        }

        double reimbursement = toDouble(res.get("low_income_reimbursement_cop"), 0);
        if (reimbursement > 0) {
            parts.add("");
            parts.add("Low Income Reimbursement: " + fmt(res, "low_income_reimbursement_cop", 2) + " COP");
        }

        parts.add("");
        parts.add("Total Payment:");
        parts.add(fmt(res, "total_cop", 2) + " COP");
        parts.add("");
        parts.add(sep);

        return "\n" + String.join("\n", parts) + "\n";
    }

    private String formatOtherSites(Map<String, Object> in) {
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> sites = (List<Map<String, Object>>)
            in.getOrDefault("other_sites", List.of());
        if (sites.isEmpty() || sites.stream().noneMatch(s -> parseDouble(s.get("amount"), 0) > 0))
            return "    None";

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < sites.size(); i++) {
            var s = sites.get(i);
            double amt = parseDouble(s.get("amount"), 0);
            if (amt <= 0) continue;
            if ("USD".equals(s.get("site_type"))) {
                sb.append("    Site ").append(i + 2).append(": ")
                  .append(String.format("%,.2f USD", amt));
            } else {
                sb.append("    Site ").append(i + 2).append(": ")
                  .append((int)amt).append(" TKS => ")
                  .append(String.format("%,.2f USD", amt / 20.0));
            }
            sb.append("\n");
        }
        return sb.toString().stripTrailing();
    }

    private String formatAdvances(Map<String, Object> in) {
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> advs = (List<Map<String, Object>>)
            in.getOrDefault("advances", List.of());
        if (advs.isEmpty() || advs.stream().noneMatch(a -> parseDouble(a.get("amount"), 0) > 0))
            return "    None";

        StringBuilder sb = new StringBuilder();
        for (var a : advs) {
            double amt = parseDouble(a.get("amount"), 0);
            if (amt <= 0) continue;
            sb.append("    ").append(a.get("date")).append(": ")
              .append(String.format("%,.2f COP", amt)).append("\n");
        }
        return sb.toString().stripTrailing();
    }

    private String formatExtras(Map<String, Object> in) {
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> ext = (List<Map<String, Object>>)
            in.getOrDefault("extras", List.of());
        if (ext.isEmpty() || ext.stream().noneMatch(a -> parseDouble(a.get("amount"), 0) > 0))
            return "    None";

        StringBuilder sb = new StringBuilder();
        for (var a : ext) {
            double amt = parseDouble(a.get("amount"), 0);
            if (amt <= 0) continue;
            sb.append("    ").append(a.get("date")).append(": ")
              .append(String.format("%,.2f COP", amt)).append("\n");
        }
        return sb.toString().stripTrailing();
    }

    private String fmt(Map<String, Object> m, String key, int decimals) {
        return String.format("%,." + decimals + "f", toDouble(m.get(key), 0));
    }

    private String fmt3(Map<String, Object> m, String key) {
        return String.format("%,.3f", toDouble(m.get(key), 0));
    }

    private String fmtInt(Map<String, Object> m, String key) {
        return String.format("%,d", (int) toDouble(m.get(key), 0));
    }

    private String fmtInt0(Map<String, Object> m, String key) {
        return String.format("%,.0f", toDouble(m.get(key), 0));
    }

    private String pct(Map<String, Object> m, String key) {
        return String.format("%.0f%%", toDouble(m.get(key), 0) * 100);
    }

    private String pct1(Map<String, Object> m, String key) {
        return String.format("%.1f%%", toDouble(m.get(key), 0) * 100);
    }

    private String center(String text, int width) {
        int pad = (width - text.length()) / 2;
        if (pad <= 0) return text;
        return " ".repeat(pad) + text;
    }

    private com.broadspec.payrollui.core.model.CalculationResult buildResultFromMap(
            Map<String, Object> res) {
        return com.broadspec.payrollui.core.model.CalculationResult.builder()
            .totalCop(toDouble(res.get("total_cop")))
            .totalUsd(toDouble(res.get("total_usd")))
            .trmBroadspecCop(toDouble(res.get("trm_broadspec_cop")))
            .transferCostCop(toDouble(res.get("transfer_cost_cop")))
            .valorBroadspecCop(toDouble(res.get("valor_broadspec_cop")))
            .finesTotal(toDouble(res.get("fines_total")))
            .finesDisplay(String.valueOf(res.getOrDefault("fines_display", "")))
            .showFines(Boolean.TRUE.equals(res.get("show_fines")))
            .advancesTotal(toDouble(res.get("advances_total")))
            .extrasTotal(toDouble(res.get("extras_total")))
            .otherSitesTotalUsd(toDouble(res.get("other_sites_total_usd")))
            .usdFromTokens(toDouble(res.get("usd_from_tokens")))
            .netUsd(toDouble(res.get("net_usd")))
            .totalUsdPrecalc(toDouble(res.get("total_usd_precalc")))
            .usdToSendPlatform(toDouble(res.get("usd_to_send_platform")))
            .lowIncomeReimbursementCop(toDouble(res.get("low_income_reimbursement_cop")))
            .date(String.valueOf(res.getOrDefault("date", "")))
            .build();
    }

    static double parseDouble(Object value) { return parseDouble(value, 0); }
    static double parseDouble(Object value, double def) {
        if (value instanceof Number n) return n.doubleValue();
        if (value instanceof String s && !s.isBlank()) {
            try { return Double.parseDouble(s.replace(",", "")); }
            catch (NumberFormatException ignored) {}
        }
        return def;
    }

    static int parseInt(Object value) { return parseInt(value, 0); }
    static int parseInt(Object value, int def) {
        if (value instanceof Number n) return n.intValue();
        if (value instanceof String s && !s.isBlank()) {
            try { return Integer.parseInt(s.replace(",", "")); }
            catch (NumberFormatException ignored) {}
        }
        return def;
    }

    static double toDouble(Object value) { return parseDouble(value, 0); }
    static double toDouble(Object value, double def) { return parseDouble(value, def); }

    record OtherSiteRow(ComboBox<String> typeCombo, TextField amountField, HBox row) {}
    record AdvanceRow(TextField dateField, TextField amountField, HBox row) {}
}
