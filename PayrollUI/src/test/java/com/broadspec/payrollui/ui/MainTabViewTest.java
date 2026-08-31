package com.broadspec.payrollui.ui;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.assertj.core.api.Assertions.assertThat;

class MainTabViewTest {

    @ParameterizedTest
    @CsvSource({
        "0,     false",
        "1,     true",
        "1000,  true",
        "2999,  true",
        "3000,  true",
        "3001,  false",
        "5000,  false",
        "10000, false"
    })
    void shouldAutoEnableRespectsThreshold(double totalTokens, boolean expected) {
        assertThat(MainTabView.shouldAutoEnable(totalTokens)).isEqualTo(expected);
    }
}
