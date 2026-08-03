package com.broadspec.payrollui.storage;

import com.broadspec.payrollui.util.Fernet;

import org.junit.jupiter.api.Test;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;

class FernetCompatibilityTest {

    @Test
    void shouldDecryptExistingVaultIndex() throws Exception {
        Path secureDir = Path.of(".secure_store");
        if (!Files.exists(secureDir)) {
            return;
        }

        Path keyPath = secureDir.resolve("key.key");
        Path indexPath = secureDir.resolve("vault_index.json.enc");

        if (!Files.exists(keyPath) || !Files.exists(indexPath)) {
            return;
        }

        String keyB64 = Files.readString(keyPath).trim();
        Fernet fernet = new Fernet(keyB64);

        byte[] enc = Files.readAllBytes(indexPath);
        assertThat(enc).isNotEmpty();

        byte[] decrypted = fernet.decrypt(enc);
        assertThat(decrypted).isNotEmpty();

        String json = new String(decrypted);
        assertThat(json).contains("vault_filename");
    }

    @Test
    void shouldDecryptExistingVaultZip() throws Exception {
        Path secureDir = Path.of(".secure_store");
        if (!Files.exists(secureDir)) {
            return;
        }

        Path keyPath = secureDir.resolve("key.key");
        Path vaultPath = secureDir.resolve("single_vault.zip.enc");

        if (!Files.exists(keyPath) || !Files.exists(vaultPath)) {
            return;
        }

        String keyB64 = Files.readString(keyPath).trim();
        Fernet fernet = new Fernet(keyB64);

        byte[] enc = Files.readAllBytes(vaultPath);
        assertThat(enc).isNotEmpty();

        byte[] decrypted = fernet.decrypt(enc);
        assertThat(decrypted).isNotEmpty();

        // Should be a valid ZIP with PK header
        assertThat(decrypted[0]).isEqualTo((byte) 'P');
        assertThat(decrypted[1]).isEqualTo((byte) 'K');
    }
}
