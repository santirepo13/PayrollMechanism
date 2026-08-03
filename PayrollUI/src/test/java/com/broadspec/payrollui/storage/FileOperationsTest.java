package com.broadspec.payrollui.storage;

import com.broadspec.payrollui.core.exception.StorageException;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class FileOperationsTest {

    private Path tempDir;
    private FileOperations fileOps;

    @BeforeEach
    void setUp() throws IOException {
        tempDir = Files.createTempDirectory("fileops_test_");
        Map<String, Object> config = Map.of("storage",
            Map.of("receiptsPath", tempDir.resolve("receipts").toString()));
        fileOps = new FileOperations(config);
    }

    @Test
    void shouldCreateDirectory() {
        Path newDir = tempDir.resolve("new_dir");
        fileOps.ensureDirectoryExists(newDir);
        assertThat(Files.exists(newDir)).isTrue();
        assertThat(Files.isDirectory(newDir)).isTrue();
    }

    @Test
    void shouldSaveAndLoadFile() throws IOException {
        Path filepath = tempDir.resolve("test.txt");
        byte[] content = "test content".getBytes();

        fileOps.saveFile(filepath, content);

        assertThat(Files.exists(filepath)).isTrue();
        assertThat(fileOps.loadFile(filepath)).isEqualTo(content);
    }

    @Test
    void shouldThrowOnLoadNonexistentFile() {
        assertThatThrownBy(() -> fileOps.loadFile(tempDir.resolve("nonexistent.txt")))
            .isInstanceOf(StorageException.class)
            .hasMessageContaining("File not found");
    }

    @Test
    void shouldDeleteFile() throws IOException {
        Path filepath = tempDir.resolve("delete_me.txt");
        Files.write(filepath, "data".getBytes());

        fileOps.deleteFile(filepath);
        assertThat(Files.exists(filepath)).isFalse();
    }

    @Test
    void shouldNotThrowOnDeleteNonexistentFile() {
        fileOps.deleteFile(tempDir.resolve("nonexistent.txt"));
    }

    @Test
    void shouldGetFileSize() throws IOException {
        Path filepath = tempDir.resolve("size_test.txt");
        byte[] content = "twelve bytes".getBytes();
        Files.write(filepath, content);

        assertThat(fileOps.getFileSize(filepath)).isEqualTo(content.length);
    }

    @Test
    void shouldReturnZeroForNonexistentFileSize() {
        assertThat(fileOps.getFileSize(tempDir.resolve("nonexistent.txt"))).isZero();
    }

    @Test
    void shouldValidateFilePath() {
        assertThat(fileOps.validateFilepath("valid/path.txt")).isTrue();
        assertThat(fileOps.validateFilepath("path\0withnull")).isFalse();
        assertThat(fileOps.validateFilepath("../../../etc/passwd")).isFalse();
    }

    @Test
    void shouldSanitizeFilename() {
        assertThat(fileOps.getSafeFilename("Test<>:\"/\\|?*Model"))
            .isEqualTo("Test_________Model");
        assertThat(fileOps.getSafeFilename("")).isEqualTo("unnamed");
    }

    @Test
    void shouldGenerateUniqueFilepath() throws IOException {
        Path existing = tempDir.resolve("test.txt");
        Files.write(existing, "data".getBytes());

        Path unique = fileOps.getUniqueFilepath(tempDir, "test.txt");
        assertThat(unique).isEqualTo(tempDir.resolve("test (1).txt"));
    }
}
