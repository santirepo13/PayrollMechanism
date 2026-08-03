package com.broadspec.payrollui.ui;

import com.broadspec.payrollui.ApplicationController;

import javafx.geometry.Side;
import javafx.scene.Scene;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.stage.Stage;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;

public class MainWindow {

    private final Stage stage;
    private final ApplicationController controller;
    private final TabPane tabPane;
    private final MainTabView mainTabView;
    private final VaultTabView vaultTabView;
    private final AdminTabView adminTabView;
    private final Set<Path> tempFiles = new HashSet<>();

    @SuppressWarnings("unchecked")
    public MainWindow(Stage stage, ApplicationController controller) {
        this.stage = stage;
        this.controller = controller;

        var uiConfig = (java.util.Map<String, Object>)
            controller.getConfig().getOrDefault("ui", java.util.Map.of());
        int width = toInt(uiConfig.get("defaultWidth"), 1900);
        int height = toInt(uiConfig.get("defaultHeight"), 1064);

        stage.setTitle("BroadSpec Payment Calculator");
        stage.setWidth(width);
        stage.setHeight(height - 40);

        tabPane = new TabPane();
        tabPane.setSide(Side.TOP);

        mainTabView = new MainTabView(controller, this);
        Tab mainTab = new Tab("Main", mainTabView.getRoot());
        mainTab.setClosable(false);

        vaultTabView = new VaultTabView(controller, this);
        Tab vaultTab = new Tab("Vault", vaultTabView.getRoot());
        vaultTab.setClosable(false);

        adminTabView = new AdminTabView(controller);
        Tab adminTab = new Tab("Admin", adminTabView.getRoot());
        adminTab.setClosable(false);

        tabPane.getTabs().addAll(mainTab, vaultTab, adminTab);

        Scene scene = new Scene(tabPane);
        scene.getStylesheets().add(
            getClass().getResource("/styles/default.css").toExternalForm());
        stage.setScene(scene);

        stage.setOnShown(e -> vaultTabView.refreshVault());
    }

    public void addTempFile(Path path) { tempFiles.add(path); }

    public void cleanupTempFiles() {
        for (Path p : tempFiles) {
            try { Files.deleteIfExists(p); } catch (IOException ignored) {}
        }
        tempFiles.clear();
    }

    public ApplicationController getController() { return controller; }

    public Stage getStage() { return stage; }

    public MainTabView getMainTabView() { return mainTabView; }

    public VaultTabView getVaultTabView() { return vaultTabView; }

    public TabPane getTabPane() { return tabPane; }

    private static int toInt(Object value, int def) {
        if (value instanceof Number n) return n.intValue();
        return def;
    }
}
