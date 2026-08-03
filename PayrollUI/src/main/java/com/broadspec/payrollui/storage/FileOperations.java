package com.broadspec.payrollui.storage;

import com.broadspec.payrollui.core.exception.StorageException;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;

public class FileOperations {

    private final Path receiptsPath;

    @SuppressWarnings("unchecked")
    public FileOperations(java.util.Map<String, Object> config) {
        java.util.Map<String, Object> storage =
            (java.util.Map<String, Object>) config.getOrDefault("storage", java.util.Map.of());
        String path = (String) storage.getOrDefault("receiptsPath", "Receipts");
        this.receiptsPath = Path.of(path);
    }

    public void ensureDirectoryExists(Path dir) {
        try {
            Files.createDirectories(dir);
        } catch (IOException e) {
            throw new StorageException("Failed to create directory " + dir + ": " + e.getMessage(), e);
        }
    }

    public void saveFile(Path filepath, byte[] content) {
        try {
            if (filepath.getParent() != null) {
                Files.createDirectories(filepath.getParent());
            }
            Files.write(filepath, content);
        } catch (IOException e) {
            throw new StorageException("Failed to save file " + filepath + ": " + e.getMessage(), e);
        }
    }

    public byte[] loadFile(Path filepath) {
        try {
            if (!Files.exists(filepath)) {
                throw new StorageException("File not found: " + filepath);
            }
            return Files.readAllBytes(filepath);
        } catch (IOException e) {
            throw new StorageException("Failed to load file " + filepath + ": " + e.getMessage(), e);
        }
    }

    public void copyFile(Path source, Path destination) {
        try {
            if (!Files.exists(source)) {
                throw new StorageException("Source file not found: " + source);
            }
            if (destination.getParent() != null) {
                Files.createDirectories(destination.getParent());
            }
            Files.copy(source, destination, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            throw new StorageException("Failed to copy file from " + source + " to " + destination + ": " + e.getMessage(), e);
        }
    }

    public void moveFile(Path source, Path destination) {
        try {
            if (!Files.exists(source)) {
                throw new StorageException("Source file not found: " + source);
            }
            if (destination.getParent() != null) {
                Files.createDirectories(destination.getParent());
            }
            Files.move(source, destination, StandardCopyOption.ATOMIC_MOVE);
        } catch (IOException e) {
            throw new StorageException("Failed to move file from " + source + " to " + destination + ": " + e.getMessage(), e);
        }
    }

    public void deleteFile(Path filepath) {
        try {
            if (Files.exists(filepath)) {
                Files.delete(filepath);
            }
        } catch (IOException e) {
            throw new StorageException("Failed to delete file " + filepath + ": " + e.getMessage(), e);
        }
    }

    public long getFileSize(Path filepath) {
        try {
            return Files.exists(filepath) ? Files.size(filepath) : 0L;
        } catch (IOException e) {
            return 0L;
        }
    }

    public boolean fileExists(Path filepath) {
        return Files.exists(filepath);
    }

    public List<Path> listFiles(Path directory, String globPattern) {
        try {
            if (!Files.exists(directory)) return List.of();
            var matcher = directory.getFileSystem().getPathMatcher("glob:" + globPattern);
            List<Path> result = new ArrayList<>();
            try (var stream = Files.list(directory)) {
                stream.filter(matcher::matches).forEach(result::add);
            }
            return result;
        } catch (IOException e) {
            throw new StorageException("Failed to list files in " + directory + ": " + e.getMessage(), e);
        }
    }

    public Path createTempFile(byte[] content, String suffix) {
        try {
            Path tmp = Files.createTempFile("broadspec_", suffix);
            Files.write(tmp, content);
            return tmp;
        } catch (IOException e) {
            throw new StorageException("Failed to create temporary file: " + e.getMessage(), e);
        }
    }

    public void openWithSystem(Path filepath) {
        try {
            if (!Files.exists(filepath)) {
                throw new StorageException("File not found: " + filepath);
            }
            String os = System.getProperty("os.name").toLowerCase();
            if (os.contains("win")) {
                new ProcessBuilder("cmd", "/c", "start", filepath.toString()).start();
            } else {
                new ProcessBuilder("xdg-open", filepath.toString()).start();
            }
        } catch (IOException e) {
            throw new StorageException("Failed to open file " + filepath + ": " + e.getMessage(), e);
        }
    }

    public boolean validateFilepath(String path) {
        if (path == null || path.contains("\0")) return false;
        Path normalized = Path.of(path).normalize();
        return !normalized.toString().contains("..");
    }

    public String getSafeFilename(String filename) {
        if (filename == null || filename.isEmpty()) return "unnamed";
        return filename.replaceAll("[<>:\"/\\\\|?*\\x00-\\x1F]", "_")
                       .replaceAll("[.\\s]+$", "");
    }

    public String getFileExtension(Path filepath) {
        String name = filepath.getFileName().toString();
        int dot = name.lastIndexOf('.');
        return dot >= 0 ? name.substring(dot).toLowerCase() : "";
    }

    public Path ensureReceiptsDirectory() {
        ensureDirectoryExists(receiptsPath);
        return receiptsPath;
    }

    public Path getUniqueFilepath(Path directory, String filename) {
        Path filepath = directory.resolve(filename);
        if (!Files.exists(filepath)) return filepath;

        int dot = filename.lastIndexOf('.');
        String base = dot >= 0 ? filename.substring(0, dot) : filename;
        String ext = dot >= 0 ? filename.substring(dot) : "";
        int counter = 1;

        while (true) {
            Path candidate = directory.resolve(base + " (" + counter + ")" + ext);
            if (!Files.exists(candidate)) return candidate;
            counter++;
        }
    }
}
