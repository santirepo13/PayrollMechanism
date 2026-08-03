package com.broadspec.payrollui;

import com.broadspec.payrollui.ui.MainWindow;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.scene.control.Alert;
import javafx.stage.Stage;

public class PayrollApplication extends Application {

    private ApplicationController controller;
    private MainWindow mainWindow;

    @Override
    public void start(Stage primaryStage) {
        try {
            controller = new ApplicationController();
            mainWindow = new MainWindow(primaryStage, controller);
            primaryStage.show();

            primaryStage.setOnCloseRequest(event -> {
                mainWindow.cleanupTempFiles();
                Platform.exit();
            });

        } catch (Exception e) {
            Alert alert = new Alert(Alert.AlertType.ERROR);
            alert.setTitle("Application Error");
            alert.setHeaderText("Failed to start");
            alert.setContentText(e.getMessage());
            alert.showAndWait();
            Platform.exit();
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
