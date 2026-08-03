package com.broadspec.payrollui.util;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class FernetTest {

    @Test
    void shouldRoundTripEncryptDecrypt() {
        byte[] rawKey = Fernet.generateKey();
        Fernet fernet = new Fernet(rawKey);

        byte[] plaintext = "Hello, BroadSpec Vault!".getBytes();

        byte[] token = fernet.encrypt(plaintext);
        assertThat(token).isNotEmpty();

        byte[] decrypted = fernet.decrypt(token);
        assertThat(decrypted).isEqualTo(plaintext);
    }

    @Test
    void shouldRoundTripWithExistingKeyFormat() {
        byte[] rawKey = Fernet.generateKey();
        String keyStr = Fernet.encodeKey(rawKey);
        Fernet fernet = new Fernet(keyStr);

        byte[] plaintext = "{\"vault_filename\":\"test.pdf\"}".getBytes();

        byte[] token = fernet.encrypt(plaintext);
        byte[] decrypted = fernet.decrypt(token);
        assertThat(decrypted).isEqualTo(plaintext);
    }
}
