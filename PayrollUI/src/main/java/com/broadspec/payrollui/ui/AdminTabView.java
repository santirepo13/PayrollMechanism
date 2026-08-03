package com.broadspec.payrollui.ui;

import com.broadspec.payrollui.ApplicationController;

import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;

public class AdminTabView {

    private final ApplicationController controller;
    private final VBox root;

    private final TextField trmOfficialField;
    private final TextField btkTrmField;
    private final TextField desiredCopField;
    private final Label requiredUsdLabel;
    private final Label retentionTaxLabel;
    private final Label transferFeeLabel;

    public AdminTabView(ApplicationController controller) {
        this.controller = controller;

        this.trmOfficialField = new TextField("0");
        this.btkTrmField = new TextField("0");
        this.desiredCopField = new TextField("0");
        this.requiredUsdLabel = new Label("");
        this.retentionTaxLabel = new Label("");
        this.transferFeeLabel = new Label("");

        root = buildLayout();
    }

    public VBox getRoot() { return root; }

    private VBox buildLayout() {
        VBox box = new VBox(10);
        box.setPadding(new Insets(10));

        Label title = new Label("COP to USD Calculator");
        title.setFont(Font.font("Arial", FontWeight.BOLD, 16));

        VBox inputFrame = new VBox(5);
        inputFrame.setPadding(new Insets(10));
        inputFrame.setStyle("-fx-border-color: lightgray;");

        inputFrame.getChildren().addAll(
            new Label("TRM Official $COP:"), trmOfficialField,
            new Label("BTK TRM $COP:"), btkTrmField,
            new Label("Desired COP Amount:"), desiredCopField
        );

        VBox notesFrame = new VBox(5);
        notesFrame.setPadding(new Insets(10));
        notesFrame.setStyle("-fx-border-color: lightgray;");
        TextArea notes = new TextArea(
            "Fees Breakdown:\n\n" +
            "\u2022 4% Retention Tax on Original USD\n" +
            "\u2022 Transfer Fee: USD 6.99 + Taxes");
        notes.setEditable(false);
        notes.setPrefRowCount(5);
        notesFrame.getChildren().add(notes);

        Button calcBtn = new Button("Calculate Required USD");
        calcBtn.setOnAction(e -> calculateUsd());

        VBox resultsFrame = new VBox(5);
        resultsFrame.setPadding(new Insets(10));
        resultsFrame.setStyle("-fx-border-color: lightgray;");
        resultsFrame.getChildren().addAll(
            new Label("Required Amount Calculations"),
            requiredUsdLabel, retentionTaxLabel, transferFeeLabel
        );

        box.getChildren().addAll(title, inputFrame, resultsFrame, notesFrame, calcBtn);

        return box;
    }

    private void calculateUsd() {
        try {
            double trmOfficial = parse(trmOfficialField.getText());
            double btkTrm = parse(btkTrmField.getText());
            double desiredCop = parse(desiredCopField.getText());

            if (trmOfficial <= 0 || btkTrm <= 0 || desiredCop <= 0) {
                throw new IllegalArgumentException("Inputs must be greater than 0");
            }

            @SuppressWarnings("unchecked")
            var calcCfg = (java.util.Map<String, Object>)
                controller.getConfig().getOrDefault("calculation", java.util.Map.of());
            @SuppressWarnings("unchecked")
            var appCfg = (java.util.Map<String, Object>)
                controller.getConfig().getOrDefault("app", java.util.Map.of());

            double baseFee = toDouble(appCfg.get("transferCost"), 6.99);
            double feeTax = toDouble(calcCfg.get("transferCostTax"), 0.19);
            double retention = calcCfg.containsKey("retentionTaxPercent")
                ? toDouble(calcCfg.get("retentionTaxPercent"), 0.04) : 0.04;

            double transferFeeUsd = baseFee * (1.0 + feeTax);
            double grossUsd = (desiredCop / btkTrm + transferFeeUsd) / (1.0 - retention);
            double retentionUsd = grossUsd * retention;

            requiredUsdLabel.setText(String.format("Required USD: %,.2f USD", grossUsd));
            requiredUsdLabel.setFont(Font.font("Arial", FontWeight.BOLD, 14));

            retentionTaxLabel.setText(String.format("Retention Tax: %,.2f USD (%,.0f COP)",
                retentionUsd, retentionUsd * btkTrm));

            transferFeeLabel.setText(String.format("Transfer Fee (including tax): %,.2f USD (%,.0f COP)",
                transferFeeUsd, transferFeeUsd * btkTrm));
        } catch (Exception e) {
            requiredUsdLabel.setText("Invalid input");
            retentionTaxLabel.setText("");
            transferFeeLabel.setText("");
            new Alert(Alert.AlertType.ERROR,
                "Please enter positive numbers for TRM Official, BTK TRM and Desired COP.")
                .showAndWait();
        }
    }

    private static double parse(String text) {
        return Double.parseDouble(text.replace(",", "").trim());
    }

    private static double toDouble(Object value, double def) {
        if (value instanceof Number n) return n.doubleValue();
        return def;
    }
}
