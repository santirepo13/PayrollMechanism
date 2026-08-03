package com.broadspec.payrollui.core.model;

import java.time.Instant;

public record VaultEntry(
    String vaultFilename,
    String origFilename,
    String modelId,
    String modelName,
    String tokens,
    String date,
    String savedAt
) {
    public VaultEntry {
        if (savedAt == null || savedAt.isEmpty()) {
            savedAt = Instant.now().toString();
        }
    }
}
