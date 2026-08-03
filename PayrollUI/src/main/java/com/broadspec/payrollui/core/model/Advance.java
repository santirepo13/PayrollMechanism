package com.broadspec.payrollui.core.model;

import java.time.LocalDate;

public record Advance(String date, double amount) {
    public Advance {
        if (date == null || date.isEmpty()) {
            date = LocalDate.now().toString();
        }
    }
}
