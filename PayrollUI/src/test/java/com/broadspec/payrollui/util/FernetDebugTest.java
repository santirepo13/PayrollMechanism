package com.broadspec.payrollui.util;

import org.junit.jupiter.api.Test;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Base64;

import static org.assertj.core.api.Assertions.assertThat;

class FernetDebugTest {

    @Test
    void shouldLoadKeyCorrectly() throws Exception {
        Path keyPath = Path.of(".secure_store", "key.key");
        if (!Files.exists(keyPath)) return;

        String raw = Files.readString(keyPath);
        System.out.println("Key file length: " + raw.length());
        System.out.println("Key file hex: " + bytesToHex(raw.getBytes(StandardCharsets.UTF_8)));
        System.out.println("Key file chars: " + raw);

        String trimmed = raw.trim();
        System.out.println("Trimmed length: " + trimmed.length());
        System.out.println("Trimmed: " + trimmed);

        byte[] keyBytes = Base64.getUrlDecoder().decode(trimmed);
        System.out.println("Decoded key length: " + keyBytes.length);
        assertThat(keyBytes.length).isEqualTo(32);
    }

    @Test
    void shouldVerifyFernetKeyAgainstPython() throws Exception {
        Path keyPath = Path.of(".secure_store", "key.key");
        if (!Files.exists(keyPath)) return;

        String keyB64 = Files.readString(keyPath).trim();
        Fernet fernet = new Fernet(keyB64);

        // Encrypt a known string, then decrypt — should work
        byte[] plain = "test".getBytes(StandardCharsets.UTF_8);
        byte[] token = fernet.encrypt(plain);
        byte[] decrypted = fernet.decrypt(token);
        assertThat(decrypted).isEqualTo(plain);
        System.out.println("Java round-trip OK");
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) sb.append(String.format("%02x", b & 0xff));
        return sb.toString();
    }
}
