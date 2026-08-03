package com.broadspec.payrollui.ui;

import com.broadspec.payrollui.ApplicationController;
import com.broadspec.payrollui.util.Formatters;

import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.layout.*;

import java.io.File;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class VaultTabView {

    private final ApplicationController controller;
    private final MainWindow mainWindow;
    private final VBox root;

    private final ListView<String> vaultListView;
    private List<Map<String, String>> vaultEntries;
    private final Label entryCountLabel;
    private final Label vaultSizeLabel;
    private final Button exportBtn, deleteBtn, importBtn, refreshBtn;

    public VaultTabView(ApplicationController controller, MainWindow mainWindow) {
        this.controller = controller;
        this.mainWindow = mainWindow;

        this.vaultListView = new ListView<>();
        this.vaultEntries = new ArrayList<>();
        this.entryCountLabel = new Label("Entries: 0");
        this.vaultSizeLabel = new Label("Vault size: 0 B");

        this.exportBtn = new Button("Export Selected");
        this.deleteBtn = new Button("Delete Selected");
        this.importBtn = new Button("Import PDFs");
        this.refreshBtn = new Button("Refresh");

        root = buildLayout();
    }

    public VBox getRoot() { return root; }

    private VBox buildLayout() {
        VBox box = new VBox(10);
        box.setPadding(new Insets(10));

        if (!controller.isVaultAvailable()) {
            box.getChildren().add(new Label(
                "Vault features are not available (cryptography package missing)"));
            return box;
        }

        HBox buttonBar = new HBox(5);
        buttonBar.getChildren().addAll(exportBtn, deleteBtn, importBtn, refreshBtn);

        vaultListView.setPrefHeight(300);
        vaultListView.getSelectionModel().setSelectionMode(SelectionMode.MULTIPLE);

        exportBtn.setOnAction(e -> handleExport());
        deleteBtn.setOnAction(e -> handleDelete());
        importBtn.setOnAction(e -> handleImport());
        refreshBtn.setOnAction(e -> refreshVault());

        HBox statsBar = new HBox(10);
        statsBar.getChildren().addAll(entryCountLabel, vaultSizeLabel);

        box.getChildren().addAll(new Label("Encrypted Vault"),
            vaultListView, buttonBar, statsBar);

        refreshVault();

        return box;
    }

    public void refreshVault() {
        if (!controller.isVaultAvailable()) return;
        try {
            vaultEntries = controller.getVaultEntries();
            vaultListView.getItems().clear();
            if (vaultEntries.isEmpty()) {
                vaultListView.getItems().add("No entries in vault");
            } else {
                for (int i = 0; i < vaultEntries.size(); i++) {
                    var entry = vaultEntries.get(i);
                    String name = entry.getOrDefault("orig_filename", "Unknown");
                    vaultListView.getItems().add((i + 1) + ". " + name);
                }
            }
            var stats = controller.getVaultStats();
            entryCountLabel.setText("Entries: " + stats.get("count"));
            vaultSizeLabel.setText("Vault size: " +
                Formatters.humanReadableSize(((Number) stats.get("size")).longValue()));
        } catch (Exception e) {
            new Alert(Alert.AlertType.ERROR,
                "Failed to refresh vault: " + e.getMessage()).showAndWait();
        }
    }

    private void handleExport() {
        if (!controller.isVaultAvailable()) return;
        var indices = vaultListView.getSelectionModel().getSelectedIndices();
        if (indices.isEmpty()) {
            new Alert(Alert.AlertType.INFORMATION,
                "Please select entries to export").showAndWait();
            return;
        }

        try {
            if (indices.size() == 1) {
                int idx = indices.get(0);
                if (idx >= vaultEntries.size()) return;
                File file = new FileChooserBuilder()
                    .title("Export PDF")
                    .extension("*.pdf")
                    .showSaveDialog(mainWindow.getStage());
                if (file == null) return;
                controller.exportFromVault(vaultEntries.get(idx).get("vault_filename"));
            } else {
                var dir = new DirectoryChooserBuilder()
                    .title("Select export directory")
                    .showDialog(mainWindow.getStage());
                if (dir == null) return;
                for (var idx : indices) {
                    if (idx < vaultEntries.size()) {
                        controller.exportFromVault(vaultEntries.get(idx).get("vault_filename"));
                    }
                }
            }
            new Alert(Alert.AlertType.INFORMATION,
                "Exported " + indices.size() + " file(s)").showAndWait();
        } catch (Exception e) {
            new Alert(Alert.AlertType.ERROR,
                "Export Error: " + e.getMessage()).showAndWait();
        }
    }

    private void handleDelete() {
        if (!controller.isVaultAvailable()) return;
        var indices = vaultListView.getSelectionModel().getSelectedIndices();
        if (indices.isEmpty()) {
            new Alert(Alert.AlertType.INFORMATION,
                "Please select entries to delete").showAndWait();
            return;
        }

        Alert confirm = new Alert(Alert.AlertType.CONFIRMATION,
            "Delete " + indices.size() + " selected entries?",
            ButtonType.YES, ButtonType.NO);
        if (confirm.showAndWait().orElse(ButtonType.NO) != ButtonType.YES) return;

        try {
            List<String> filenames = new ArrayList<>();
            for (var idx : indices) {
                if (idx < vaultEntries.size()) {
                    filenames.add(vaultEntries.get(idx).get("vault_filename"));
                }
            }
            int deleted = controller.deleteFromVault(filenames);
            refreshVault();
            new Alert(Alert.AlertType.INFORMATION,
                "Deleted " + deleted + " file(s)").showAndWait();
        } catch (Exception e) {
            new Alert(Alert.AlertType.ERROR,
                "Delete Error: " + e.getMessage()).showAndWait();
        }
    }

    private void handleImport() {
        if (!controller.isVaultAvailable()) return;
        var files = new FileChooserBuilder()
            .title("Select PDF files to import")
            .extension("*.pdf")
            .showOpenMultipleDialog(mainWindow.getStage());
        if (files == null || files.isEmpty()) return;

        try {
            List<Path> paths = files.stream().map(File::toPath).toList();
            int[] result = controller.importToVault(paths);
            if (result[1] > 0) {
                new Alert(Alert.AlertType.WARNING,
                    "Imported " + result[0] + " file(s)\nFailed: " + result[1]).showAndWait();
            } else {
                new Alert(Alert.AlertType.INFORMATION,
                    "Successfully imported " + result[0] + " file(s)").showAndWait();
            }
            refreshVault();
        } catch (Exception e) {
            new Alert(Alert.AlertType.ERROR,
                "Import Error: " + e.getMessage()).showAndWait();
        }
    }

    private static class FileChooserBuilder {
        private String title;
        private String extension;

        FileChooserBuilder title(String t) { this.title = t; return this; }
        FileChooserBuilder extension(String e) { this.extension = e; return this; }

        File showSaveDialog(javafx.stage.Window w) {
            javafx.stage.FileChooser fc = new javafx.stage.FileChooser();
            if (title != null) fc.setTitle(title);
            if (extension != null) fc.getExtensionFilters().add(
                new javafx.stage.FileChooser.ExtensionFilter("PDF", extension));
            return fc.showSaveDialog(w);
        }

        List<File> showOpenMultipleDialog(javafx.stage.Window w) {
            javafx.stage.FileChooser fc = new javafx.stage.FileChooser();
            if (title != null) fc.setTitle(title);
            if (extension != null) fc.getExtensionFilters().add(
                new javafx.stage.FileChooser.ExtensionFilter("PDF", extension));
            return fc.showOpenMultipleDialog(w);
        }
    }

    private static class DirectoryChooserBuilder {
        private String title;

        DirectoryChooserBuilder title(String t) { this.title = t; return this; }

        File showDialog(javafx.stage.Window w) {
            javafx.stage.DirectoryChooser dc = new javafx.stage.DirectoryChooser();
            if (title != null) dc.setTitle(title);
            return dc.showDialog(w);
        }
    }
}
