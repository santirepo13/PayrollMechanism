package com.broadspec.payrollui.storage;

import com.broadspec.payrollui.core.exception.VaultException;
import com.broadspec.payrollui.core.model.VaultEntry;
import com.broadspec.payrollui.util.Fernet;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

public class VaultRepository {

    private final Path secureStoreDir;
    private final Path keyPath;
    private final Path singleVaultPath;
    private final Path vaultIndexPath;
    private final Fernet fernet;
    private final ObjectMapper objectMapper;

    private List<Map<String, String>> vaultIndex;

    @SuppressWarnings("unchecked")
    public VaultRepository(Map<String, Object> config) {
        Map<String, Object> storage =
            (Map<String, Object>) config.getOrDefault("storage", Map.of());
        String vaultPath = (String) storage.getOrDefault("vaultPath", ".secure_store");

        this.secureStoreDir = Path.of(vaultPath);
        this.keyPath = secureStoreDir.resolve("key.key");
        this.singleVaultPath = secureStoreDir.resolve("single_vault.zip.enc");
        this.vaultIndexPath = secureStoreDir.resolve("vault_index.json.enc");
        this.objectMapper = new ObjectMapper();
        this.vaultIndex = new ArrayList<>();

        try {
            Files.createDirectories(secureStoreDir);
            if (Files.exists(keyPath)) {
                String keyB64 = Files.readString(keyPath).trim();
                this.fernet = new Fernet(keyB64);
            } else {
                byte[] rawKey = Fernet.generateKey();
                this.fernet = new Fernet(rawKey);
                Files.writeString(keyPath, Fernet.encodeKey(rawKey));
            }
        } catch (IOException e) {
            throw new VaultException("Failed to initialize vault: " + e.getMessage(), e);
        }

        try {
            loadIndex();
        } catch (Exception e) {
            try {
                rebuildIndexFromVault();
            } catch (Exception e2) {
                vaultIndex = new ArrayList<>();
            }
        }
    }

    public List<Map<String, String>> loadIndex() {
        try {
            if (!Files.exists(vaultIndexPath)) {
                vaultIndex = new ArrayList<>();
                return vaultIndex;
            }
            byte[] enc = Files.readAllBytes(vaultIndexPath);
            if (enc.length == 0) {
                vaultIndex = new ArrayList<>();
                return vaultIndex;
            }
            try {
                byte[] dec = fernet.decrypt(enc);
                vaultIndex = objectMapper.readValue(dec,
                    new TypeReference<List<Map<String, String>>>() {});
                return vaultIndex;
            } catch (Exception tokenErr) {
                throw new VaultException(
                    "Vault index exists but cannot be decrypted (invalid key): " + tokenErr.getMessage(), tokenErr);
            }
        } catch (Exception e) {
            throw new VaultException("Failed to load vault index: " + e.getMessage(), e);
        }
    }

    public void rebuildIndexFromVault() {
        try {
            if (!Files.exists(singleVaultPath)) {
                vaultIndex = new ArrayList<>();
                saveIndex();
                return;
            }
            byte[] vaultBytes = decryptVault();
            if (vaultBytes.length == 0) {
                vaultIndex = new ArrayList<>();
                saveIndex();
                return;
            }

            List<Map<String, String>> newIndex = new ArrayList<>();
            try (ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(vaultBytes))) {
                ZipEntry entry;
                while ((entry = zis.getNextEntry()) != null) {
                    Map<String, String> parsed = parseFilenameMetadata(entry.getName());
                    Map<String, String> meta = new LinkedHashMap<>();
                    meta.put("vault_filename", entry.getName());
                    meta.put("orig_filename", entry.getName());
                    meta.put("model_id", parsed.getOrDefault("model_id", ""));
                    meta.put("model_name", parsed.getOrDefault("model_name", ""));
                    meta.put("tokens", parsed.getOrDefault("tokens", ""));
                    meta.put("date", parsed.getOrDefault("date", ""));
                    meta.put("saved_at", null);
                    newIndex.add(meta);
                }
            }
            vaultIndex = newIndex;
            saveIndex();
        } catch (Exception e) {
            throw new VaultException("Failed to rebuild index from vault: " + e.getMessage(), e);
        }
    }

    public VaultEntry addFile(Path sourceFilepath, Map<String, String> metadata) {
        try {
            byte[] fileBytes = Files.readAllBytes(sourceFilepath);
            String origName = sourceFilepath.getFileName().toString();
            return addBytes(fileBytes, origName, metadata);
        } catch (IOException e) {
            throw new VaultException("Failed to add file to vault: " + e.getMessage(), e);
        }
    }

    public VaultEntry addBytes(byte[] fileBytes, String origFilename,
                                Map<String, String> metadata) {
        try {
            byte[] existingZipBytes = decryptVault();
            Set<String> existingNames = getZipEntryNames(existingZipBytes);

            String safeName = sanitizeFilename(origFilename);
            String candidate = safeName;
            int counter = 1;
            while (existingNames.contains(candidate)) {
                int dot = safeName.lastIndexOf('.');
                String base = dot >= 0 ? safeName.substring(0, dot) : safeName;
                String ext = dot >= 0 ? safeName.substring(dot) : "";
                candidate = base + " (" + counter + ")" + ext;
                counter++;
            }

            ByteArrayOutputStream newZipBaos = new ByteArrayOutputStream();
            try (ZipOutputStream zos = new ZipOutputStream(newZipBaos)) {
                if (existingZipBytes.length > 0) {
                    copyZipEntries(existingZipBytes, zos);
                }
                zos.putNextEntry(new ZipEntry(candidate));
                zos.write(fileBytes);
                zos.closeEntry();
            }

            byte[] newZipBytes = newZipBaos.toByteArray();
            byte[] encryptedToken = fernet.encrypt(newZipBytes);
            Files.write(singleVaultPath, encryptedToken);

            String now = Instant.now().toString();
            VaultEntry entry = new VaultEntry(
                candidate, origFilename,
                metadata.getOrDefault("model_id", ""),
                metadata.getOrDefault("model_name", ""),
                metadata.getOrDefault("tokens", ""),
                metadata.getOrDefault("date", ""),
                now
            );

            Map<String, String> entryMeta = new LinkedHashMap<>();
            entryMeta.put("vault_filename", entry.vaultFilename());
            entryMeta.put("orig_filename", entry.origFilename());
            entryMeta.put("model_id", entry.modelId());
            entryMeta.put("model_name", entry.modelName());
            entryMeta.put("tokens", entry.tokens());
            entryMeta.put("date", entry.date());
            entryMeta.put("saved_at", entry.savedAt());
            vaultIndex.add(entryMeta);

            saveIndex();
            return entry;
        } catch (Exception e) {
            throw new VaultException("Failed to add file to vault: " + e.getMessage(), e);
        }
    }

    public byte[] retrieveFile(String vaultFilename) {
        try {
            byte[] vaultBytes = decryptVault();
            try (ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(vaultBytes))) {
                ZipEntry entry;
                while ((entry = zis.getNextEntry()) != null) {
                    if (entry.getName().equals(vaultFilename)) {
                        return zis.readAllBytes();
                    }
                }
            }
            throw new VaultException("File not found in vault: " + vaultFilename);
        } catch (IOException e) {
            throw new VaultException("Failed to retrieve file from vault: " + e.getMessage(), e);
        }
    }

    public int deleteFiles(List<String> vaultFilenames) {
        if (vaultFilenames == null || vaultFilenames.isEmpty()) return 0;

        try {
            byte[] vaultBytes = decryptVault();
            Set<String> toDelete = new HashSet<>(vaultFilenames);

            ByteArrayOutputStream newZipBaos = new ByteArrayOutputStream();
            try (ZipOutputStream zos = new ZipOutputStream(newZipBaos);
                 ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(vaultBytes))) {
                ZipEntry entry;
                while ((entry = zis.getNextEntry()) != null) {
                    if (!toDelete.contains(entry.getName())) {
                        zos.putNextEntry(new ZipEntry(entry.getName()));
                        zos.write(zis.readAllBytes());
                        zos.closeEntry();
                    }
                }
            }

            byte[] newZipBytes = newZipBaos.toByteArray();
            byte[] encryptedToken = fernet.encrypt(newZipBytes);
            Files.write(singleVaultPath, encryptedToken);

            int originalCount = vaultIndex.size();
            vaultIndex.removeIf(entry -> toDelete.contains(entry.get("vault_filename")));
            int deletedCount = originalCount - vaultIndex.size();

            saveIndex();
            return deletedCount;
        } catch (Exception e) {
            throw new VaultException("Failed to delete files from vault: " + e.getMessage(), e);
        }
    }

    public List<Map<String, String>> getAllEntries() {
        return new ArrayList<>(vaultIndex);
    }

    public long getVaultSize() {
        try {
            return Files.exists(singleVaultPath) ? Files.size(singleVaultPath) : 0L;
        } catch (IOException e) {
            return 0L;
        }
    }

    public boolean isAvailable() {
        return fernet != null;
    }

    public Path getSecureStoreDir() {
        return secureStoreDir;
    }

    private byte[] decryptVault() {
        try {
            if (!Files.exists(singleVaultPath)) return new byte[0];
            byte[] enc = Files.readAllBytes(singleVaultPath);
            if (enc.length == 0) return new byte[0];
            return fernet.decrypt(enc);
        } catch (Exception e) {
            if (e.getMessage() != null && e.getMessage().contains("invalid key")) {
                throw new VaultException("Cannot decrypt vault (invalid key)", e);
            }
            throw new VaultException("Failed to decrypt vault: " + e.getMessage(), e);
        }
    }

    private void saveIndex() {
        try {
            byte[] json = objectMapper.writeValueAsBytes(vaultIndex);
            byte[] token = fernet.encrypt(json);
            Files.write(vaultIndexPath, token);
        } catch (Exception e) {
            throw new VaultException("Failed to save vault index: " + e.getMessage(), e);
        }
    }

    private Set<String> getZipEntryNames(byte[] zipBytes) {
        Set<String> names = new HashSet<>();
        if (zipBytes.length == 0) return names;
        try (ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(zipBytes))) {
            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                names.add(entry.getName());
            }
        } catch (IOException ignored) {}
        return names;
    }

    private void copyZipEntries(byte[] zipBytes, ZipOutputStream targetZos) throws IOException {
        try (ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(zipBytes))) {
            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                targetZos.putNextEntry(new ZipEntry(entry.getName()));
                targetZos.write(zis.readAllBytes());
                targetZos.closeEntry();
            }
        }
    }

    public static Map<String, String> parseFilenameMetadata(String filename) {
        Map<String, String> result = new LinkedHashMap<>();
        result.put("model_id", "");
        result.put("model_name", "");
        result.put("tokens", "");
        result.put("date", "");

        if (filename == null || filename.isEmpty()) return result;

        String base = filename.replaceAll("\\\\", "/");
        int lastSlash = base.lastIndexOf('/');
        if (lastSlash >= 0) base = base.substring(lastSlash + 1);
        base = base.replaceAll("\\.pdf$", "");

        Matcher dateMatcher = Pattern.compile("(\\d{4}-\\d{2}-\\d{2})$").matcher(base);
        if (dateMatcher.find()) {
            result.put("date", dateMatcher.group(1));
            base = base.substring(0, dateMatcher.start()).replaceAll("\\s*-\\s*$", "");
        }

        String[] parts = java.util.Arrays.stream(base.split("\\s*-\\s*"))
            .map(String::trim).filter(s -> !s.isEmpty()).toArray(String[]::new);

        if (parts.length >= 1) result.put("model_id", parts[0]);

        int tokenIndex = -1;
        for (int i = parts.length - 1; i > 0; i--) {
            if (Pattern.compile("\\b\\d[\\d,.]*\\s*(TKS)?\\b", Pattern.CASE_INSENSITIVE)
                    .matcher(parts[i]).find()) {
                tokenIndex = i;
                break;
            }
        }

        if (tokenIndex != -1) {
            result.put("tokens", parts[tokenIndex]);
            result.put("model_name", tokenIndex > 1
                ? String.join(" - ", java.util.Arrays.copyOfRange(parts, 1, tokenIndex))
                : (parts.length > 1 ? parts[1] : ""));
        } else {
            if (parts.length >= 3) {
                result.put("tokens", parts[parts.length - 1]);
                result.put("model_name", String.join(" - ",
                    java.util.Arrays.copyOfRange(parts, 1, parts.length - 1)));
            } else if (parts.length > 1) {
                result.put("model_name", String.join(" - ",
                    java.util.Arrays.copyOfRange(parts, 1, parts.length)));
            }
        }

        return result;
    }

    public static String sanitizeFilename(String name) {
        if (name == null || name.isEmpty()) return "unnamed";
        return name.replaceAll("[<>:\"/\\\\|?*\\x00-\\x1F]", "_")
                   .replaceAll("[.\\s]+$", "");
    }
}
