package com.broadspec.payrollui.util;

import com.broadspec.payrollui.core.model.CalculationResult;

import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

class PdfProtocolsTest {

    @Test
    void shouldGenerateFilenameWithResult() {
        Map<String, Object> data = Map.of(
            "model_id", "12345",
            "model_name", "Test Model",
            "tokens", 1000,
            "other_sites", List.of(
                Map.of("site_type", "USD", "amount", 100),
                Map.of("site_type", "TKS", "amount", 200)
            )
        );

        CalculationResult result = CalculationResult.builder()
            .totalCop(1000000).totalUsd(250).usdToSendPlatform(280.5).date("2025-01-20").build();

        String filename = PdfProtocols.generateFilename(data, result);

        assertThat(filename).contains("12345");
        assertThat(filename).contains("Test Model");
        assertThat(filename).contains("3200 TKS");
        assertThat(filename).contains("280.500 USD");
        assertThat(filename).contains("1.000.000 COP");
        assertThat(filename).endsWith(".pdf");
    }

    @Test
    void shouldGenerateFilenameWithoutResult() {
        Map<String, Object> data = Map.of(
            "model_id", "12345",
            "model_name", "Test Model",
            "tokens", 1000,
            "other_sites", List.of()
        );

        String filename = PdfProtocols.generateFilename(data, null);

        assertThat(filename).contains("12345");
        assertThat(filename).contains("Test Model");
        assertThat(filename).contains(LocalDate.now().toString());
        assertThat(filename).endsWith(".pdf");
    }
}
