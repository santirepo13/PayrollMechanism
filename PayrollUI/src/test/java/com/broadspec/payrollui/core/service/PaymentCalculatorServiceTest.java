package com.broadspec.payrollui.core.service;

import com.broadspec.payrollui.core.model.CalculationResult;
import com.broadspec.payrollui.core.model.Advance;
import com.broadspec.payrollui.core.model.OtherSite;
import com.broadspec.payrollui.core.model.PaymentData;
import com.broadspec.payrollui.core.exception.ValidationException;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class PaymentCalculatorServiceTest {

    private PaymentCalculatorService calculator;

    @BeforeEach
    void setUp() {
        Map<String, Object> config = Map.of(
            "calculation", Map.of(
                "tokenToUsdRate", 20.0,
                "trmAdjustment", 300.0,
                "fineAmount", 30000.0,
                "transferCostTax", 0.19
            ),
            "app", Map.of("transferCost", 6.99)
        );
        calculator = new PaymentCalculatorService(config);
    }

    @Test
    void shouldCalculateBasicPayment() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0,
            List.of(), List.of(), List.of(),
            0, 0.0, false, false);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.totalCop()).isPositive();
        assertThat(result.totalUsd()).isPositive();
        assertThat(result.trmBroadspecCop()).isEqualTo(3700.0);
        assertThat(result.usdFromTokens()).isEqualTo(50.0);
        assertThat(result.netUsd()).isEqualTo(35.0);
    }

    @Test
    void shouldCalculateWithUsdOtherSites() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0,
            List.of(new OtherSite("USD", 100)),
            List.of(), List.of(),
            0, 0.0, false, false);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.otherSitesTotalUsd()).isEqualTo(70.0);
    }

    @Test
    void shouldCalculateWithTksOtherSites() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0,
            List.of(new OtherSite("TKS", 200)),
            List.of(), List.of(),
            0, 0.0, false, false);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.otherSitesTotalUsd()).isEqualTo(7.0);
    }

    @Test
    void shouldCalculateWithAdvances() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0,
            List.of(), List.of(new Advance("2025-01-01", 100000)),
            List.of(), 0, 0.0, false, false);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.advancesTotal()).isEqualTo(100000);
    }

    @Test
    void shouldApplyFinesForStudioWorker() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.6, 0.0,
            List.of(), List.of(), List.of(),
            2, 0.0, false, false);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.finesTotal()).isEqualTo(60000);
        assertThat(result.showFines()).isTrue();
    }

    @Test
    void shouldDisableFinesForHomeWorker() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0,
            List.of(), List.of(), List.of(),
            2, 0.0, false, false);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.finesTotal()).isEqualTo(60000);
        assertThat(result.showFines()).isFalse();
    }

    @Test
    void shouldUseCustomFineAmount() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.6, 0.0,
            List.of(), List.of(), List.of(),
            0, 50000, false, false);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.finesTotal()).isEqualTo(50000);
        assertThat(result.finesDisplay()).contains("Custom");
    }

    @ParameterizedTest
    @CsvSource({
        "9999,  0.0",
        "10000, 0.03",
        "12499, 0.03",
        "12500, 0.045",
        "14999, 0.045",
        "15000, 0.06",
        "17499, 0.06",
        "17500, 0.08",
        "19999, 0.08",
        "20000, 0.10",
        "30000, 0.10"
    })
    void shouldCalculateCorrectBonusTier(double totalTokens, double expectedBonus) {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, (int) totalTokens, 0.6, 0.0,
            List.of(), List.of(), List.of(),
            0, 0.0, false, false);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.bonusPercentage()).isEqualTo(expectedBonus);
    }

    @Test
    void shouldDisableBonusWhenFlagSet() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 25000, 0.6, 0.0,
            List.of(), List.of(), List.of(),
            0, 0.0, false, true);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.bonusPercentage()).isEqualTo(0.0);
        assertThat(result.bonusAmountUsd()).isEqualTo(0.0);
    }

    @Test
    void shouldRejectInvalidData() {
        PaymentData data = new PaymentData("", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0,
            List.of(), List.of(), List.of(),
            0, 0.0, false, false);

        assertThatThrownBy(() -> calculator.calculate(data))
            .isInstanceOf(ValidationException.class)
            .hasMessageContaining("Model ID is required");
    }

    @Test
    void shouldNotApplyReimbursementWhenFlagOff() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0,
            List.of(), List.of(), List.of(),
            0, 0.0, false, false, 0.0, false);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.lowIncomeReimbursementCop()).isEqualTo(0.0);
        assertThat(result.totalCop()).isPositive();
    }

    @Test
    void shouldApplyReimbursementEqualToTransferCostWhenFlagOn() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0,
            List.of(), List.of(), List.of(),
            0, 0.0, false, false, 0.0, true);

        CalculationResult result = calculator.calculate(data);

        double expectedTransferCostCop = 6.99 * (1.0 + 0.19) * 4100.0;
        assertThat(result.lowIncomeReimbursementCop())
            .isCloseTo(expectedTransferCostCop, org.assertj.core.data.Offset.offset(0.01));
        assertThat(result.transferCostCop())
            .isCloseTo(expectedTransferCostCop, org.assertj.core.data.Offset.offset(0.01));
        assertThat(result.totalCop()).isPositive();
    }

    @Test
    void shouldIncreaseTotalCopByReimbursementAmount() {
        PaymentData dataOff = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0,
            List.of(), List.of(), List.of(),
            0, 0.0, false, false, 0.0, false);
        PaymentData dataOn = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0,
            List.of(), List.of(), List.of(),
            0, 0.0, false, false, 0.0, true);

        CalculationResult resultOff = calculator.calculate(dataOff);
        CalculationResult resultOn = calculator.calculate(dataOn);

        assertThat(resultOn.totalCop() - resultOff.totalCop())
            .isCloseTo(resultOn.lowIncomeReimbursementCop(), org.assertj.core.data.Offset.offset(0.01));
    }
}
