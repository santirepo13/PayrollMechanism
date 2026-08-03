# BroadSpec Payment Calculator → Java + JavaFX Conversion

> Refactoring the Python/Tkinter desktop application to Java 26 + JavaFX 26.
> Package: `com.broadspec.PayrollUI`
> Companion API project (future): `com.broadspec.PayrollApi`

---

## 1. Project Setup

### 1.1 Maven Coordinates

```xml
<groupId>com.broadspec</groupId>
<artifactId>PayrollUI</artifactId>
<version>1.0.0</version>
<packaging>jar</packaging>
<name>BroadSpec Payment Calculator</name>
```

### 1.2 Parent POM (optional multi-module)

```
PayrollMechanism/
├── pom.xml                          # parent: com.broadspec:PayrollMechanism:1.0.0
├── payroll-ui/
│   ├── pom.xml                      # com.broadspec:PayrollUI
│   └── src/
│       ├── main/java/com/broadspec/payrollui/
│       ├── main/resources/
│       └── test/java/com/broadspec/payrollui/
├── payroll-api/                     # future: com.broadspec:PayrollApi
└── docs/
```

### 1.3 `payroll-ui/pom.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.broadspec</groupId>
        <artifactId>PayrollMechanism</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId>PayrollUI</artifactId>

    <properties>
        <java.version>26</java.version>
        <javafx.version>26.0.0</javafx.version>
        <pdfbox.version>3.0.4</pdfbox.version>
        <fernet.version>1.5.0</fernet.version>
        <snakeyaml.version>2.3</snakeyaml.version>
        <junit.version>5.11.4</junit.version>
        <mockito.version>5.15.2</mockito.version>
        <slf4j.version>2.0.16</slf4j.version>
    </properties>

    <dependencies>
        <!-- JavaFX -->
        <dependency>
            <groupId>org.openjfx</groupId>
            <artifactId>javafx-controls</artifactId>
            <version>${javafx.version}</version>
        </dependency>
        <dependency>
            <groupId>org.openjfx</groupId>
            <artifactId>javafx-graphics</artifactId>
            <version>${javafx.version}</version>
        </dependency>
        <dependency>
            <groupId>org.openjfx</groupId>
            <artifactId>javafx-swing</artifactId>
            <version>${javafx.version}</version>
        </dependency>

        <!-- PDF Generation & Processing (replaces ReportLab + PyMuPDF) -->
        <dependency>
            <groupId>org.apache.pdfbox</groupId>
            <artifactId>pdfbox</artifactId>
            <version>${pdfbox.version}</version>
        </dependency>

        <!-- Fernet Encryption (compatible with Python cryptography.Fernet) -->
        <dependency>
            <groupId>com.macasaet.fernet</groupId>
            <artifactId>fernet-java8</artifactId>
            <version>${fernet.version}</version>
        </dependency>

        <!-- YAML Configuration (replaces PyYAML) -->
        <dependency>
            <groupId>org.yaml</groupId>
            <artifactId>snakeyaml</artifactId>
            <version>${snakeyaml.version}</version>
        </dependency>

        <!-- Logging -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>${slf4j.version}</version>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-simple</artifactId>
            <version>${slf4j.version}</version>
            <scope>runtime</scope>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <version>${mockito.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-junit-jupiter</artifactId>
            <version>${mockito.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.13.0</version>
                <configuration>
                    <source>${java.version}</source>
                    <target>${java.version}</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.openjfx</groupId>
                <artifactId>javafx-maven-plugin</artifactId>
                <version>0.0.8</version>
                <configuration>
                    <mainClass>com.broadspec.payrollui.PayrollApplication</mainClass>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.5.2</version>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## 2. Fernet Vault Compatibility (CRITICAL)

### 2.1 Existing Vault Format

The Python vault uses `cryptography.Fernet` with the following structure:

```
.secure_store/
├── key.key              # 44-char base64url-encoded Fernet key (32 bytes raw)
├── key.bin              # Raw key bytes
├── single_vault.zip.enc # Fernet-encrypted ZIP containing all PDF receipts
└── vault_index.json.enc # Fernet-encrypted JSON array of vault entry metadata
```

**Fernet token format** (Python `cryptography` library):
- Version byte: `0x80`
- Timestamp: 8 bytes (big-endian, seconds since epoch)
- IV: 16 bytes (random)
- Ciphertext: variable (AES-128-CBC, PKCS7 padding, with HMAC-SHA256 appended)
- HMAC: 32 bytes (SHA-256 over version + timestamp + IV + ciphertext)

### 2.2 Java Fernet Library

Use `com.macasaet.fernet:fernet-java8` which:
- Implements the full Fernet specification
- Reads/writes tokens compatible with Python `cryptography.Fernet`
- Handles base64url encoding, timestamp validation, HMAC verification
- Supports custom `Validator` for cross-implementation compatibility (optional max-clock-skew buffer)

### 2.3 Key Loading

```java
// Load existing Fernet key from .secure_store/key.key (base64url)
Path keyPath = secureStoreDir.resolve("key.key");
String keyBase64Url = Files.readString(keyPath).trim();
Key key = new Key(keyBase64Url);

// Or load from key.bin (raw bytes)
Path keyBinPath = secureStoreDir.resolve("key.bin");
byte[] rawKey = Files.readAllBytes(keyBinPath);
Key key = new Key(rawKey);

// If neither exists (first run), generate new key
Key key = Key.generateKey();
Files.writeString(secureStoreDir.resolve("key.key"), key.serialise());
```

### 2.4 Decryption Flow (reading existing vault)

```java
// 1. Load index
byte[] encryptedIndex = Files.readAllBytes(vaultIndexPath);
Token indexToken = Token.fromBytes(encryptedIndex);
byte[] decryptedIndexBytes = indexToken.validateAndDecrypt(key, validator);
String indexJson = new String(decryptedIndexBytes, StandardCharsets.UTF_8);
// Parse JSON array → List<VaultEntryMetadata>

// 2. Load vault ZIP
byte[] encryptedVault = Files.readAllBytes(singleVaultPath);
Token vaultToken = Token.fromBytes(encryptedVault);
byte[] decryptedVaultBytes = vaultToken.validateAndDecrypt(key, validator);
// Read as ZIP → extract individual PDFs

// 3. Read individual file from vault
ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(decryptedVaultBytes));
ZipEntry entry;
while ((entry = zis.getNextEntry()) != null) {
    if (entry.getName().equals(vaultFilename)) {
        byte[] pdfBytes = zis.readAllBytes();
        // Use pdfBytes for preview or export
    }
}
```

### 2.5 Encryption Flow (writing to vault)

```java
// 1. Add PDF bytes to ZIP
ByteArrayOutputStream baos = new ByteArrayOutputStream();
ZipOutputStream zos = new ZipOutputStream(baos);
// Copy all existing entries first (if vault exists)
ZipEntry newEntry = new ZipEntry(sanitizedFilename);
zos.putNextEntry(newEntry);
zos.write(pdfBytes);
zos.closeEntry();
zos.close();

// 2. Encrypt ZIP with Fernet
byte[] zipBytes = baos.toByteArray();
Token encryptedToken = Token.generate(key, zipBytes);
Files.write(singleVaultPath, encryptedToken.serialise());

// 3. Encrypt index JSON with Fernet
String indexJson = objectMapper.writeValueAsString(vaultIndex);
Token encryptedIndexToken = Token.generate(key, indexJson.getBytes(StandardCharsets.UTF_8));
Files.write(vaultIndexPath, encryptedIndexToken.serialise());
```

### 2.6 Cross-Compatibility Verification

**Test class: `FernetCompatibilityTest.java`**

```java
@Test
void shouldDecryptExistingPythonVaultIndex() {
    // Copy .secure_store/ from Python project to test resources
    // Load key.key → decrypt vault_index.json.enc → parse JSON
    // Assert: at least 1 entry with expected fields (model_id, model_name, etc.)
}

@Test
void shouldDecryptExistingPythonVaultPdf() {
    // Decrypt single_vault.zip.enc → extract first PDF
    // Assert: PDF bytes > 0, can be opened by PDFBox
}

@Test
void shouldProducePythonCompatibleOutput() {
    // Write test PDF to vault → encrypt with Java Fernet
    // Provide instructions for Python to read back (manual or integration test)
    // Assert: output Token format matches Fernet spec
}
```

---

## 3. Class Mapping

### 3.1 Data Models (records)

| Python (dataclass) | Java (record) |
|---|---|
| `PaymentData` (`models.py:32`) | `PaymentData` |
| `CalculationResult` (`models.py:59`) | `CalculationResult` |
| `Advance` (`models.py:7`) | `Advance` |
| `OtherSite` (`models.py:18`) | `OtherSite` |
| `VaultEntry` (`models.py:123`) | `VaultEntry` |

```java
// PaymentData.java
package com.broadspec.payrollui.core.model;

import java.util.List;

public record PaymentData(
    String modelId,
    String modelName,
    double trmOfficialCop,
    double btkTrmCop,
    int tokens,
    double percentage,
    double previousFortnightUsd,
    List<OtherSite> otherSites,
    List<Advance> advances,
    List<Advance> extras,
    int finesCount,
    double customFineCop,
    boolean overrideHighTokensTrm,
    boolean disableBonus,
    double bonusTokens        // 0 = all tokens
) {
    public PaymentData {
        if (otherSites == null) otherSites = List.of();
        if (advances == null) advances = List.of();
        if (extras == null) extras = List.of();
    }

    // Backward-compatible constructor (without bonusTokens)
    public PaymentData(
        String modelId, String modelName, double trmOfficialCop, double btkTrmCop,
        int tokens, double percentage, double previousFortnightUsd,
        List<OtherSite> otherSites, List<Advance> advances, List<Advance> extras,
        int finesCount, double customFineCop, boolean overrideHighTokensTrm, boolean disableBonus
    ) {
        this(modelId, modelName, trmOfficialCop, btkTrmCop, tokens, percentage,
             previousFortnightUsd, otherSites, advances, extras, finesCount,
             customFineCop, overrideHighTokensTrm, disableBonus, 0.0);
    }
}
```

```java
// OtherSite.java
package com.broadspec.payrollui.core.model;

public record OtherSite(String siteType, double amount) {
    public double getUsdEquivalent(double tokenToUsdRate) {
        return "USD".equalsIgnoreCase(siteType)
            ? amount
            : amount / tokenToUsdRate;
    }
}
```

```java
// Advance.java
package com.broadspec.payrollui.core.model;

public record Advance(String date, double amount) {}
```

```java
// CalculationResult.java — uses @Builder for the large number of fields
package com.broadspec.payrollui.core.model;

import lombok.Builder;
import lombok.Value;

@Value
@Builder
public class CalculationResult {
    double totalCop;
    double totalUsd;
    double trmBroadspecCop;
    double transferCostCop;
    double valorBroadspecCop;
    double finesTotal;
    String finesDisplay;
    boolean showFines;
    double advancesTotal;
    double extrasTotal;
    double otherSitesTotalUsd;
    double usdFromTokens;
    double netUsd;
    double totalUsdPrecalc;
    double usdToSendPlatform;
    double btkTrmCop;
    String date;
    double totalTokensAllSites;
    double bonusPercentage;
    double bonusAmountUsd;
    double bonusAmountCop;
    double originalPercentage;
    double finalPercentage;
    double bonusTokensUsed;
    double nonBonusTokens;
    double bonusRatio;
}
```

```java
// VaultEntry.java
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
```

### 3.2 Services

| Python Class | Java Class | Notes |
|---|---|---|
| `PaymentCalculator` | `PaymentCalculatorService` | Singleton, config-injected via constructor |
| `ReceiptGenerator` | `ReceiptGeneratorService` | PDFBox replaces ReportLab canvas |
| `VaultRepository` | `VaultRepository` | Fernet-java8, same ZIP-in-Fernet pattern |
| `FileOperations` | `FileOperations` | `java.nio.file.Files` + `Path` API |
| `PDFPreviewer` | `PdfPreviewService` | PDFBox `PDFRenderer` → `BufferedImage` → JavaFX `WritableImage` |

### 3.3 Utilities

| Python | Java | Notes |
|---|---|---|
| `formatters.py` | `Formatters` (static methods) | Currency formatting, filename parsing |
| `validators.py` | `Validators` (static methods) | Input validation (returns `List<String>`) |
| `pdf_protocols.py` | `PdfProtocols` (static methods) | Filename generation, sanitization |

### 3.4 Exceptions

| Python | Java |
|---|---|
| `BroadSpecError` (base) | `BroadSpecException` extends `RuntimeException` |
| `CalculationError` | `CalculationException` |
| `VaultError` | `VaultException` |
| `ValidationError` | `ValidationException` |
| `ConfigurationError` | `ConfigurationException` |
| `StorageError` | `StorageException` |
| `ReceiptGenerationError` | `ReceiptGenerationException` |
| `UIError` | `UiException` |

### 3.5 UI Components

| Python (`tkinter`) | Java (`javafx`) |
|---|---|
| `ApplicationController` (MVC) | `ApplicationController` (same pattern) |
| `BroadSpecGUI` | `PayrollApplication` extends `Application` |
| `WindowSetup` | `MainWindow` — `Stage`/`Scene`/`TabPane` setup |
| `MainTabUI` | `MainTabView` (programmatic, `GridPane` layout) |
| `VaultTabUI` | `VaultTabView` |
| `AdminTabUI` | `AdminTabView` |
| `CalculationHandler` | `CalculationHandler` |
| `PDFSaver` | `PdfSaver` |
| `ModelImageSaver` | `ModelImageSaver` |
| `ResolutionManager` | `ResolutionManager` |
| `PDFPreviewHandler` | `PdfPreviewHandler` |
| `ttk.Notebook` | `TabPane` with 3 `Tab` nodes |
| `tk.Text` (receipt) | `TextArea` (monospaced, non-editable) |
| `ttk.Entry` | `TextField` / `Spinner` |
| `ttk.Combobox` | `ComboBox` |
| `ttk.Checkbutton` | `CheckBox` |
| `ttk.Button` | `Button` |
| `tk.Canvas` (PDF preview) | `ScrollPane` > `Canvas` or `ImageView` |
| `tk.Listbox` (vault) | `ListView<VaultEntry>` or `TableView<VaultEntry>` |
| `tk.filedialog` | `FileChooser` / `DirectoryChooser` |
| `messagebox` | `Alert` |

---

## 4. Directory Structure

```
payroll-ui/src/main/java/com/broadspec/payrollui/
│
├── PayrollApplication.java            # JavaFX Application.launch(), Stage setup
├── ApplicationController.java         # MVC controller (orchestrates services + UI)
│
├── core/
│   ├── model/
│   │   ├── PaymentData.java           # record
│   │   ├── CalculationResult.java     # @Builder
│   │   ├── Advance.java              # record
│   │   ├── OtherSite.java            # record
│   │   └── VaultEntry.java           # record
│   ├── service/
│   │   ├── PaymentCalculatorService.java
│   │   └── ReceiptGeneratorService.java
│   └── exception/
│       ├── BroadSpecException.java
│       ├── CalculationException.java
│       ├── VaultException.java
│       ├── ValidationException.java
│       ├── ConfigurationException.java
│       ├── StorageException.java
│       ├── ReceiptGenerationException.java
│       └── UiException.java
│
├── ui/
│   ├── MainWindow.java                # Stage, Scene, TabPane, global layout
│   ├── MainTabView.java               # Main calculator tab (GridPane)
│   ├── VaultTabView.java              # Vault management tab
│   ├── AdminTabView.java              # COP→USD calculator tab
│   └── handler/
│       ├── CalculationHandler.java    # Collect form data → calculate → display
│       ├── PdfSaver.java             # Save PDF to vault
│       ├── ModelImageSaver.java      # Screenshot receipt as JPEG/PNG
│       ├── PdfPreviewHandler.java    # PDFBox → WritableImage → ImageView
│       └── ResolutionManager.java    # Resolution toggle + scaling
│
├── storage/
│   ├── VaultRepository.java          # Fernet-compatible vault CRUD
│   └── FileOperations.java           # File I/O with validation
│
└── util/
    ├── Formatters.java                # formatCurrencyCop, formatCurrencyUsd, sanitizeFilename, etc.
    ├── Validators.java                # validateNumericInput, validatePercentage, validateDate, etc.
    └── PdfProtocols.java              # generateFilename, sanitizeFilename
```

### Test Structure

```
payroll-ui/src/test/java/com/broadspec/payrollui/
│
├── core/
│   └── service/
│       ├── PaymentCalculatorServiceTest.java
│       └── ReceiptGeneratorServiceTest.java
├── storage/
│   ├── VaultRepositoryTest.java
│   ├── FernetCompatibilityTest.java   # Cross-compat with Python vault
│   └── FileOperationsTest.java
└── util/
    ├── ValidatorsTest.java
    ├── FormattersTest.java
    └── PdfProtocolsTest.java
```

---

## 5. Business Logic Preservation

All calculation formulas map 1:1 from `broadspec/core/calculator.py`.

### 5.1 `PaymentCalculatorService.java`

```java
public class PaymentCalculatorService {
    private final double tokenToUsdRate;    // config.yaml: calculation.token_to_usd_rate (20.0)
    private final double trmAdjustment;     // config.yaml: calculation.trm_adjustment (300)
    private final double fineAmount;        // config.yaml: calculation.fine_amount (30000)
    private final double transferCost;      // config.yaml: app.transfer_cost (6.99)
    private final double transferCostTax;   // config.yaml: calculation.transfer_cost_tax (0.19)

    // Constructor: reads from config

    public CalculationResult calculate(PaymentData data) {
        // 1. Total tokens across all sites
        double otherSitesTokensTotal = data.otherSites().stream()
            .mapToDouble(site -> "USD".equalsIgnoreCase(site.siteType())
                ? site.amount() * tokenToUsdRate
                : site.amount())
            .sum();
        double totalTokensAllSites = data.tokens() + otherSitesTokensTotal;

        // 2. Bonus percentage
        double bonusPercentage = data.disableBonus()
            ? 0.0
            : calculateBonusPercentage(totalTokensAllSites);

        // 3. Final percentage
        double originalPercentage = data.percentage() > 1
            ? data.percentage() / 100.0
            : data.percentage();
        double finalPercentage = originalPercentage + bonusPercentage;

        // 4. TRM adjustment
        double trmAdjustmentUsed = data.overrideHighTokensTrm()
            ? trmAdjustment
            : (totalTokensAllSites >= 3000 ? 200 : trmAdjustment);
        double trmBroadspecCop = data.trmOfficialCop() - trmAdjustmentUsed;

        // 5. Transfer cost
        double transferCostUsd = transferCost + (transferCost * transferCostTax);
        double transferCostCop = transferCostUsd * data.btkTrmCop();

        // 6. USD from tokens
        double usdFromTokens = data.tokens() / tokenToUsdRate;
        double netUsd = usdFromTokens * finalPercentage;

        // 7. Other sites USD
        double otherSitesTotalUsdRaw = data.otherSites().stream()
            .mapToDouble(site -> site.getUsdEquivalent(tokenToUsdRate))
            .sum();
        double otherSitesTotalUsd = otherSitesTotalUsdRaw * finalPercentage;

        // 8. Total USD precalc
        double totalUsdPrecalc = netUsd + otherSitesTotalUsd + data.previousFortnightUsd();

        // 9. BroadSpec value
        double valorBroadspecCop = (totalUsdPrecalc * trmBroadspecCop) - transferCostCop;

        // 10. Fines
        FinesResult fines = calculateFines(data);

        // 11. Advances and extras
        double advancesTotal = data.advances().stream().mapToDouble(Advance::amount).sum();
        double extrasTotal = data.extras().stream().mapToDouble(Advance::amount).sum();

        // 12. Final totals
        double totalCop = valorBroadspecCop - advancesTotal - fines.total() + extrasTotal;
        double totalUsd = totalCop / trmBroadspecCop;

        // 13. Bonus amounts
        double totalUsdRaw = usdFromTokens + otherSitesTotalUsdRaw;
        double bonusAmountUsd = totalUsdRaw * bonusPercentage;
        double bonusAmountCop = bonusAmountUsd * trmBroadspecCop;

        // 14. Platform USD
        double tokenValueCop = data.btkTrmCop() * 0.05;
        double usdToSendPlatform = ((tokenValueCop > 0 && tokenToUsdRate > 0)
            ? ((totalCop + transferCostCop) / tokenValueCop) / tokenToUsdRate
            : 0.0);

        // 15. Bonus token range handling (bonus_tokens field)
        double bonusTokensUsed, nonBonusTokens, bonusRatio;
        if (data.disableBonus()) {
            bonusTokensUsed = 0;
        } else if (data.bonusTokens() > 0) {
            bonusTokensUsed = Math.min(data.bonusTokens(), totalTokensAllSites);
        } else {
            bonusTokensUsed = totalTokensAllSites;
        }
        nonBonusTokens = totalTokensAllSites - bonusTokensUsed;
        bonusRatio = totalTokensAllSites > 0 ? bonusTokensUsed / totalTokensAllSites : 0;

        return CalculationResult.builder()
            .totalCop(totalCop)
            .totalUsd(totalUsd)
            .trmBroadspecCop(trmBroadspecCop)
            .transferCostCop(transferCostCop)
            .valorBroadspecCop(valorBroadspecCop)
            .finesTotal(fines.total())
            .finesDisplay(fines.display())
            .showFines(fines.showFines())
            .advancesTotal(advancesTotal)
            .extrasTotal(extrasTotal)
            .otherSitesTotalUsd(otherSitesTotalUsd)
            .usdFromTokens(usdFromTokens)
            .netUsd(netUsd)
            .totalUsdPrecalc(totalUsdPrecalc)
            .usdToSendPlatform(usdToSendPlatform)
            .btkTrmCop(data.btkTrmCop())
            .date(data.date() != null ? data.date() : java.time.LocalDate.now().toString())
            .totalTokensAllSites(totalTokensAllSites)
            .bonusPercentage(bonusPercentage)
            .bonusAmountUsd(bonusAmountUsd)
            .bonusAmountCop(bonusAmountCop)
            .originalPercentage(originalPercentage)
            .finalPercentage(finalPercentage)
            .bonusTokensUsed(bonusTokensUsed)
            .nonBonusTokens(nonBonusTokens)
            .bonusRatio(bonusRatio)
            .build();
    }

    private double calculateBonusPercentage(double totalTokens) {
        if (totalTokens >= 20000) return 0.10;   // 10%
        if (totalTokens >= 17500) return 0.08;   // 8%
        if (totalTokens >= 15000) return 0.06;   // 6%
        if (totalTokens >= 12500) return 0.045;  // 4.5%
        if (totalTokens >= 10000) return 0.03;   // 3%
        return 0.0;
    }

    private FinesResult calculateFines(PaymentData data) {
        double percent = data.percentage() > 1 ? data.percentage() / 100.0 : data.percentage();
        boolean showFines = percent <= 0.60;

        double finesTotal;
        String finesDisplay;
        if (data.customFineCop() > 0) {
            finesTotal = data.customFineCop();
            finesDisplay = String.format("Custom: %,.0f COP", finesTotal);
        } else {
            finesTotal = data.finesCount() * fineAmount;
            finesDisplay = String.format("%d fines x %,.0f = %,.0f COP",
                data.finesCount(), fineAmount, finesTotal);
        }
        return new FinesResult(finesTotal, finesDisplay, showFines);
    }
}
```

### 5.2 `ReceiptGeneratorService.java` (PDFBox replaces ReportLab)

```java
// Key PDFBox APIs:
PDDocument document = new PDDocument();
PDPage page = new PDPage(PDRectangle.LETTER);
document.addPage(page);
PDPageContentStream cs = new PDPageContentStream(document, page);

// Text positioning (replaces canvas.drawString)
cs.beginText();
cs.newLineAtOffset(50, 700);
cs.setFont(PDType1Font.COURIER_BOLD, 16);
cs.showText("BROADSPEC PAYMENT RECEIPTS");
cs.endText();

// Table-like layout using manual positioning
cs.beginText();
cs.newLineAtOffset(50, 650);
cs.setFont(PDType1Font.COURIER, 9);
cs.showText("Model ID: 12345");
cs.newLineAtOffset(0, -12);
cs.showText("Model: Test Model");
// ... etc.
cs.endText();

cs.close();
document.save(filepath);
document.close();

// In-memory generation (for vault storage):
ByteArrayOutputStream baos = new ByteArrayOutputStream();
PDDocument document = ...;
document.save(baos);
document.close();
byte[] pdfBytes = baos.toByteArray();  // → vaultRepository.addBytes()
```

---

## 6. PDF Preview (PDFBox → JavaFX)

```java
// PdfPreviewService.java
public class PdfPreviewService {
    private PDDocument document;
    private int currentPage = 0;
    private double zoomLevel = 1.0;

    public boolean openPdf(Path pdfPath) {
        document = Loader.loadPDF(pdfPath.toFile());
        currentPage = 0;
        return true;
    }

    public boolean openPdfBytes(byte[] data) {
        document = Loader.loadPDF(data);
        currentPage = 0;
        return true;
    }

    public WritableImage getPageImage() {
        PDFRenderer renderer = new PDFRenderer(document);
        // Render at specified DPI for zoom (72 DPI base × zoom)
        int dpi = (int) (72 * zoomLevel);
        BufferedImage bim = renderer.renderImageWithDPI(currentPage, dpi);

        // Convert BufferedImage → JavaFX WritableImage
        WritableImage fxImage = new WritableImage(bim.getWidth(), bim.getHeight());
        PixelWriter pw = fxImage.getPixelWriter();
        for (int y = 0; y < bim.getHeight(); y++) {
            for (int x = 0; x < bim.getWidth(); x++) {
                int argb = bim.getRGB(x, y);
                pw.setArgb(x, y, argb);
            }
        }
        return fxImage;
    }

    public void setZoom(double zoom) { this.zoomLevel = zoom; }
    public int getPageCount() { return document.getNumberOfPages(); }
    public void setCurrentPage(int page) { this.currentPage = page; }
    public void close() { document.close(); }
}
```

---

## 7. Model Image Saver (Node Snapshot)

```java
// ModelImageSaver.java
public class ModelImageSaver {
    public void saveModelImage(TextArea modelTextArea, String baseFilename) {
        // Render the TextArea content as WritableImage (JavaFX snapshot)
        WritableImage snapshot = modelTextArea.snapshot(
            new SnapshotParameters(), null);

        // Convert to BufferedImage for ImageIO
        BufferedImage bim = SwingFXUtils.fromFXImage(snapshot, null);

        // Crop to actual text content
        // ... (trim whitespace from bottom, exclude BTK TRM lines conceptually)

        // Save as JPEG
        Path imgDir = Path.of("img");
        Files.createDirectories(imgDir);
        Path outPath = imgDir.resolve(baseFilename + ".jpg");
        ImageIO.write(bim, "JPEG", outPath.toFile());
    }
}
```

---

## 8. UI Architecture (JavaFX)

### 8.1 `PayrollApplication.java` (Entry Point)

```java
public class PayrollApplication extends Application {
    @Override
    public void start(Stage primaryStage) {
        ApplicationController controller = new ApplicationController();
        MainWindow mainWindow = new MainWindow(primaryStage, controller);
        primaryStage.show();

        // Cleanup on close
        primaryStage.setOnCloseRequest(event -> {
            mainWindow.cleanupTempFiles();
            controller.shutdown();
        });
    }

    public static void main(String[] args) {
        launch(args);
    }
}
```

### 8.2 `MainWindow.java` (TabPane Layout)

```java
public class MainWindow {
    private final Stage stage;
    private final ApplicationController controller;
    private final TabPane tabPane;
    private final MainTabView mainTabView;
    private final VaultTabView vaultTabView;
    private final AdminTabView adminTabView;

    // Temp file tracking for cleanup
    private final Set<Path> tempFiles = new HashSet<>();

    public MainWindow(Stage stage, ApplicationController controller) {
        this.stage = stage;
        this.controller = controller;

        stage.setTitle("BroadSpec Payment Calculator");
        stage.setWidth(1900);
        stage.setHeight(1024);  // 1064 - 40 taskbar

        tabPane = new TabPane();

        Tab mainTab = new Tab("Main");
        mainTabView = new MainTabView(controller, this);
        mainTab.setContent(mainTabView.getRoot());
        mainTab.setClosable(false);

        Tab vaultTab = new Tab("Vault");
        vaultTabView = new VaultTabView(controller, this);
        vaultTab.setContent(vaultTabView.getRoot());
        vaultTab.setClosable(false);

        Tab adminTab = new Tab("Admin");
        adminTabView = new AdminTabView(controller, this);
        adminTab.setContent(adminTabView.getRoot());
        adminTab.setClosable(false);

        tabPane.getTabs().addAll(mainTab, vaultTab, adminTab);

        Scene scene = new Scene(tabPane);
        scene.getStylesheets().add(
            getClass().getResource("/styles/default.css").toExternalForm());
        stage.setScene(scene);
    }

    public void addTempFile(Path path) { tempFiles.add(path); }

    public void cleanupTempFiles() {
        for (Path p : tempFiles) {
            try { Files.deleteIfExists(p); } catch (IOException ignored) {}
        }
        tempFiles.clear();
    }
}
```

### 8.3 `MainTabView.java` (Programmatic GridPane)

```java
public class MainTabView {
    private final SplitPane receiptPane;
    private final TextArea fullReceiptText;
    private final TextArea modelReceiptText;

    // Input fields
    private final TextField modelIdField;
    private final TextField modelNameField;
    private final TextField trmOfficialField;
    private final TextField btkTrmField;
    private final TextField tokensField;
    private final ComboBox<String> percentageCombo;
    private final TextField previousFortnightUsdField;
    private final TextField finesCountField;
    private final TextField customFineField;
    private final CheckBox overrideHighTokensTrmCheck;
    private final CheckBox disableBonusCheck;

    // Dynamic list containers
    private final VBox advancesContainer;
    private final List<AdvanceRow> advanceRows = new ArrayList<>();
    private final VBox extrasContainer;
    private final List<ExtraRow> extraRows = new ArrayList<>();
    private final VBox otherSitesContainer;
    private final List<OtherSiteRow> otherSiteRows = new ArrayList<>();

    // Buttons
    private final Button calculateBtn;
    private final Button clearBtn;
    private final Button saveModelImageBtn;
    private final Button savePdfBtn;

    // Build with GridPane
    public MainTabView(ApplicationController controller, MainWindow mainWindow) {
        // ... GridPane layout mirroring main_tab_ui.py:_create_input_fields()
        // Left column: scrollable input area (ScrollPane > VBox)
        // Right columns: receipt display (SplitPane with two TextArea)
        // Bottom: button bar (HBox)
    }
}

// Helper record for dynamic rows
record AdvanceRow(TextField dateField, TextField amountField, HBox row, Button removeBtn) {}
record ExtraRow(TextField dateField, TextField amountField, HBox row, Button removeBtn) {}
record OtherSiteRow(ComboBox<String> typeCombo, TextField amountField, HBox row, Button removeBtn) {}
```

### 8.4 `VaultTabView.java` (ListView + PDF Preview)

```java
public class VaultTabView {
    private final TableView<VaultEntry> vaultTable;   // replaces tk.Listbox
    private final Label entryCountLabel;
    private final Label vaultSizeLabel;
    private final ImageView pdfPreviewView;            // replaces tk.Canvas
    private final ComboBox<String> zoomCombo;          // 50%-200%
    private final Button prevPageBtn, nextPageBtn;
    private final Label pageLabel;                     // "1 / 2"
    private final Button exportBtn, deleteBtn, importBtn, refreshBtn, resolutionBtn;

    // ... layout with VBox
}
```

### 8.5 `AdminTabView.java` (GridPane form)

```java
public class AdminTabView {
    private final TextField trmOfficialField;
    private final TextField btkTrmField;
    private final TextField desiredCopField;
    private final Label requiredUsdLabel;
    private final Label retentionTaxLabel;
    private final Label transferFeeLabel;
    private final Button calculateBtn;
    private final Button exitBtn;
}
```

---

## 9. UI Component Parity Table

| # | Python Requirement (`srs.md` UI-00x) | JavaFX Implementation |
|---|---|---|
| UI-001 | 3-tab interface (Main, Vault, Admin) | `TabPane` with 3 `Tab` nodes, `setClosable(false)` |
| UI-002 | Input fields with labels | `GridPane`: `Label` + `TextField`/`ComboBox` pairs |
| UI-003 | Two receipt panels side by side | `SplitPane` > `TextArea` (left) + `TextArea` (right), both `setEditable(false)`, monospaced font |
| UI-004 | Dynamic add/remove rows with "X" | `VBox` > `HBox` per row, `Button("✕")` removes row |
| UI-005 | Vault management buttons + list | `TableView<VaultEntry>` + `HBox` of `Button`s |
| UI-006 | PDF preview + zoom + navigation | `ImageView` in `ScrollPane` + `ComboBox` (zoom) + prev/next `Button`s + `Label` (page counter) |
| UI-007 | Admin COP→USD calculator | `GridPane` form + results `Label`s |
| UI-008 | Fee breakdown text | `TextArea` (read-only, styled) |
| UI-009 | Checkboxes (override TRM, disable bonus) | `CheckBox` (2 instances) |
| UI-010 | Resolution toggle | `Button` → resize `Stage`, scale fonts via CSS classes or manual font size multipliers |
| UI-011 | Enable/disable fines on percentage change | `ComboBox.valueProperty().addListener()` → `finesCountField.setDisable()`, label update |
| UI-012 | Scrollable input area | `ScrollPane` wrapping left-side `VBox` input form |
| UI-013 | Clean up temp files on exit | `Stage.setOnCloseRequest()` → `cleanupTempFiles()` |

---

## 10. Configuration

### 10.1 `application.yaml` (replaces `config.yaml`)

```yaml
app:
  name: "BroadSpec Payment Calculator"
  version: "1.0.0"
  transferCost: 6.99

ui:
  defaultWidth: 1900
  defaultHeight: 1064
  pdfPreviewEnabled: true
  resolutions:
    - name: "1920x1080"
      width: 1920
      height: 1080
    - name: "1366x768"
      width: 1366
      height: 768
  themes:
    - name: "default"
      colors:
        primary: "#007bff"
        secondary: "#6c757d"
        background: "#ffffff"
        text: "#000000"

storage:
  vaultPath: ".secure_store"
  receiptsPath: "Receipts"
  encryptionAlgorithm: "Fernet"

calculation:
  tokenToUsdRate: 20.0
  trmAdjustment: 300
  fineAmount: 30000
  transferCostTax: 0.19
```

### 10.2 Loading in Java

```java
// ApplicationController._loadConfiguration()
InputStream is = getClass().getClassLoader()
    .getResourceAsStream("application.yaml");
Yaml yaml = new Yaml();
Map<String, Object> config = yaml.load(is);
```

---

## 11. Exception Hierarchy

```java
// BroadSpecException.java
public class BroadSpecException extends RuntimeException {
    public BroadSpecException(String message) { super(message); }
    public BroadSpecException(String message, Throwable cause) { super(message, cause); }
}

// CalculationException.java
public class CalculationException extends BroadSpecException {
    public CalculationException(String message) { super(message); }
}

// VaultException.java
public class VaultException extends BroadSpecException {
    public VaultException(String message) { super(message); }
}

// ValidationException.java
public class ValidationException extends BroadSpecException {
    public ValidationException(String message) { super(message); }
}

// ConfigurationException.java
public class ConfigurationException extends BroadSpecException {
    public ConfigurationException(String message) { super(message); }
}

// StorageException.java
public class StorageException extends BroadSpecException {
    public StorageException(String message) { super(message); }
}

// ReceiptGenerationException.java
public class ReceiptGenerationException extends BroadSpecException {
    public ReceiptGenerationException(String message) { super(message); }
}

// UiException.java
public class UiException extends BroadSpecException {
    public UiException(String message) { super(message); }
}
```

---

## 12. Utility Classes

### 12.1 `Formatters.java`

```java
public final class Formatters {
    private Formatters() {}

    public static String formatCurrencyCop(double amount) {
        return String.format("$%,.0f COP", amount);
    }

    public static String formatCurrencyUsd(double amount) {
        return String.format("$%,.2f", amount);
    }

    public static String sanitizeFilename(String name) {
        if (name == null || name.isEmpty()) return "unnamed";
        return name.replaceAll("[<>:\"/\\\\|?*\\x00-\\x1F]", "_")
                   .replaceAll("[\s.]+$", "");  // trailing spaces/dots
    }

    public static String humanReadableSize(long bytes) {
        // Same logic as Python: B → KB → MB → GB → TB
    }

    public static Map<String, String> parseFilenameMetadata(String filename) {
        // Same logic as formatters.py:parse_filename_metadata
    }
}
```

### 12.2 `Validators.java`

```java
public final class Validators {
    private Validators() {}

    public static List<String> validatePaymentData(PaymentData data) {
        List<String> errors = new ArrayList<>();

        if (data.modelId() == null || data.modelId().isBlank())
            errors.add("Model ID is required");
        if (data.trmOfficialCop() <= 0)
            errors.add("TRM Official COP must be greater than 0");
        if (data.btkTrmCop() <= 0)
            errors.add("BTK TRM COP must be greater than 0");
        if (data.tokens() < 0)
            errors.add("Tokens cannot be negative");

        double percent = data.percentage() > 1 ? data.percentage() / 100.0 : data.percentage();
        if (percent <= 0 || percent > 1)
            errors.add("Percentage must be between 0 and 1");

        if (data.previousFortnightUsd() < 0)
            errors.add("Previous Fortnight USD cannot be negative");
        if (data.finesCount() < 0)
            errors.add("Fines count cannot be negative");
        if (data.customFineCop() < 0)
            errors.add("Custom fine amount cannot be negative");

        for (int i = 0; i < data.advances().size(); i++) {
            if (data.advances().get(i).amount() < 0)
                errors.add("Advance " + (i+1) + " amount cannot be negative");
        }
        for (int i = 0; i < data.extras().size(); i++) {
            if (data.extras().get(i).amount() < 0)
                errors.add("Extra " + (i+1) + " amount cannot be negative");
        }
        for (int i = 0; i < data.otherSites().size(); i++) {
            var site = data.otherSites().get(i);
            if (site.amount() < 0)
                errors.add("Other Site " + (i+1) + " amount cannot be negative");
            if (!List.of("USD", "TKS").contains(site.siteType().toUpperCase()))
                errors.add("Other Site " + (i+1) + " type must be USD or TKS");
        }
        return errors;
    }
}
```

### 12.3 `PdfProtocols.java`

```java
public final class PdfProtocols {
    private PdfProtocols() {}

    public static String generateFilename(
            Map<String, Object> inputData, CalculationResult result) {
        // Same logic as pdf_protocols.py:generate_filename
        // Format: {model_id} - {model_name} - {tokens} TKS - {usd} USD - {cop} COP - {date}.pdf
    }
}
```

---

## 13. File Operations

```java
// FileOperations.java
public class FileOperations {
    private final Path receiptsPath;

    public FileOperations(Map<String, Object> config) {
        Map<String, Object> storage = (Map<String, Object>) config.get("storage");
        String path = storage != null ? (String) storage.get("receiptsPath") : "Receipts";
        this.receiptsPath = Path.of(path);
    }

    public void ensureDirectoryExists(Path dir) throws IOException {
        Files.createDirectories(dir);
    }

    public void saveFile(Path filepath, byte[] content) throws IOException {
        Files.createDirectories(filepath.getParent());
        Files.write(filepath, content);
    }

    public byte[] loadFile(Path filepath) throws IOException {
        if (!Files.exists(filepath))
            throw new StorageException("File not found: " + filepath);
        return Files.readAllBytes(filepath);
    }

    public boolean validateFilepath(String path) {
        if (path == null) return false;
        if (path.contains("\0")) return false;
        // Check for path traversal
        Path normalized = Path.of(path).normalize();
        return !normalized.toString().contains("..");
    }

    public String getSafeFilename(String filename) {
        if (filename == null || filename.isEmpty()) return "unnamed";
        return filename.replaceAll("[<>:\"/\\\\|?*\\x00-\\x1F]", "_")
                       .replaceAll("[.\\s]+$", "");
    }

    public Path ensureReceiptsDirectory() throws IOException {
        Files.createDirectories(receiptsPath);
        return receiptsPath;
    }

    public Path getUniqueFilepath(Path directory, String filename) {
        Path filepath = directory.resolve(filename);
        if (!Files.exists(filepath)) return filepath;

        String base = filename.replaceAll("\\.[^.]+$", "");
        String ext = filename.substring(filename.lastIndexOf('.'));
        int counter = 1;
        while (true) {
            Path candidate = directory.resolve(base + " (" + counter + ")" + ext);
            if (!Files.exists(candidate)) return candidate;
            counter++;
        }
    }

    public void openWithSystem(Path filepath) throws IOException {
        if (!Files.exists(filepath))
            throw new StorageException("File not found: " + filepath);

        if (System.getProperty("os.name").toLowerCase().contains("win")) {
            new ProcessBuilder("cmd", "/c", "start", filepath.toString()).start();
        } else {
            new ProcessBuilder("xdg-open", filepath.toString()).start();
        }
    }
}
```

---

## 14. Vault Repository

```java
// VaultRepository.java
public class VaultRepository {
    private final Path secureStoreDir;
    private final Path keyPath;
    private final Path singleVaultPath;
    private final Path vaultIndexPath;
    private final Key fernetKey;
    private final Validator<String> fernetValidator;
    private List<VaultEntryMetadata> vaultIndex;

    public VaultRepository(Map<String, Object> config) {
        Map<String, Object> storage = (Map<String, Object>) config.get("storage");
        String vaultPath = storage != null ? (String) storage.get("vaultPath") : ".secure_store";
        this.secureStoreDir = Path.of(vaultPath);
        this.keyPath = secureStoreDir.resolve("key.key");
        this.singleVaultPath = secureStoreDir.resolve("single_vault.zip.enc");
        this.vaultIndexPath = secureStoreDir.resolve("vault_index.json.enc");

        // Load or generate key
        try {
            Files.createDirectories(secureStoreDir);
            if (Files.exists(keyPath)) {
                String keyB64 = Files.readString(keyPath).trim();
                this.fernetKey = new Key(keyB64);
            } else {
                this.fernetKey = Key.generateKey();
                Files.writeString(keyPath, fernetKey.serialise());
            }
        } catch (IOException e) {
            throw new VaultException("Failed to initialize vault: " + e.getMessage(), e);
        }

        // Lenient validator for cross-implementation compatibility
        this.fernetValidator = new StringValidator() {
            @Override
            public TemporalAmount getTimeToLive() {
                return java.time.Duration.ofDays(365 * 100); // effectively no expiry
            }
            @Override
            public TemporalAmount getMaxClockSkew() {
                return java.time.Duration.ofMinutes(10); // tolerance for clock drift
            }
        };

        this.vaultIndex = new ArrayList<>();
        loadIndex();
    }

    public List<VaultEntryMetadata> loadIndex() {
        if (!Files.exists(vaultIndexPath)) {
            vaultIndex = new ArrayList<>();
            return vaultIndex;
        }
        try {
            byte[] enc = Files.readAllBytes(vaultIndexPath);
            Token token = Token.fromBytes(enc);
            byte[] dec = token.validateAndDecrypt(fernetKey, fernetValidator);
            // Parse JSON
            ObjectMapper mapper = new ObjectMapper();
            vaultIndex = mapper.readValue(dec, new TypeReference<List<VaultEntryMetadata>>() {});
            return vaultIndex;
        } catch (Exception e) {
            throw new VaultException("Failed to load vault index: " + e.getMessage(), e);
        }
    }

    public VaultEntry addBytes(byte[] fileBytes, String origFilename,
                                Map<String, String> metadata) {
        // Decrypt existing vault ZIP (or start empty)
        byte[] existingZipBytes = decryptVault();

        // Build new ZIP (copy existing entries + add new)
        ByteArrayOutputStream newZipBaos = new ByteArrayOutputStream();
        try (ZipOutputStream zos = new ZipOutputStream(newZipBaos)) {
            // Copy existing entries
            if (existingZipBytes != null && existingZipBytes.length > 0) {
                try (ZipInputStream zis = new ZipInputStream(
                        new ByteArrayInputStream(existingZipBytes))) {
                    ZipEntry entry;
                    while ((entry = zis.getNextEntry()) != null) {
                        zos.putNextEntry(new ZipEntry(entry.getName()));
                        zos.write(zis.readAllBytes());
                        zos.closeEntry();
                    }
                }
            }

            // Determine unique filename
            Set<String> existingNames = getZipEntryNames(existingZipBytes);
            String safeName = Formatters.sanitizeFilename(origFilename);
            String candidate = safeName;
            int counter = 1;
            while (existingNames.contains(candidate)) {
                String base = safeName.replaceAll("\\.[^.]+$", "");
                String ext = safeName.substring(safeName.lastIndexOf('.'));
                candidate = base + " (" + counter + ")" + ext;
                counter++;
            }

            // Add new entry
            zos.putNextEntry(new ZipEntry(candidate));
            zos.write(fileBytes);
            zos.closeEntry();
        } catch (IOException e) {
            throw new VaultException("Failed to add file to vault: " + e.getMessage(), e);
        }

        // Encrypt new ZIP
        byte[] newZipBytes = newZipBaos.toByteArray();
        try {
            Token encryptedToken = Token.generate(fernetKey, newZipBytes);
            Files.write(singleVaultPath, encryptedToken.serialise());
        } catch (IOException e) {
            throw new VaultException("Failed to encrypt vault: " + e.getMessage(), e);
        }

        // Update index
        VaultEntryMetadata entryMeta = new VaultEntryMetadata(
            candidate, origFilename,
            metadata.getOrDefault("modelId", ""),
            metadata.getOrDefault("modelName", ""),
            metadata.getOrDefault("tokens", ""),
            metadata.getOrDefault("date", ""),
            Instant.now().toString()
        );
        vaultIndex.add(entryMeta);
        saveIndex();

        return new VaultEntry(candidate, origFilename,
            entryMeta.modelId(), entryMeta.modelName(),
            entryMeta.tokens(), entryMeta.date(), entryMeta.savedAt());
    }

    public byte[] retrieveFile(String vaultFilename) {
        byte[] vaultBytes = decryptVault();
        try (ZipInputStream zis = new ZipInputStream(
                new ByteArrayInputStream(vaultBytes))) {
            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                if (entry.getName().equals(vaultFilename)) {
                    return zis.readAllBytes();
                }
            }
        } catch (IOException e) {
            throw new VaultException("Failed to retrieve file from vault: " + e.getMessage(), e);
        }
        throw new VaultException("File not found in vault: " + vaultFilename);
    }

    public int deleteFiles(List<String> vaultFilenames) {
        // Same pattern: decrypt ZIP → rebuild excluding deleted → encrypt → update index
        // ... (mirrors Python impl)
    }

    public List<VaultEntryMetadata> getAllEntries() {
        return new ArrayList<>(vaultIndex);
    }

    public long getVaultSize() {
        try {
            return Files.exists(singleVaultPath) ? Files.size(singleVaultPath) : 0L;
        } catch (IOException e) {
            return 0L;
        }
    }

    private byte[] decryptVault() {
        if (!Files.exists(singleVaultPath)) return new byte[0];
        try {
            byte[] enc = Files.readAllBytes(singleVaultPath);
            if (enc.length == 0) return new byte[0];
            Token token = Token.fromBytes(enc);
            return token.validateAndDecrypt(fernetKey, fernetValidator);
        } catch (Exception e) {
            throw new VaultException("Cannot decrypt vault (invalid key): " + e.getMessage(), e);
        }
    }

    private void saveIndex() {
        try {
            ObjectMapper mapper = new ObjectMapper();
            byte[] json = mapper.writeValueAsBytes(vaultIndex);
            Token token = Token.generate(fernetKey, json);
            Files.write(vaultIndexPath, token.serialise());
        } catch (Exception e) {
            throw new VaultException("Failed to save vault index: " + e.getMessage(), e);
        }
    }
}
```

---

## 15. Testing Strategy

### 15.1 `PaymentCalculatorServiceTest.java`

```java
@ExtendWith(MockitoExtension.class)
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
            4000.0, 4100.0, 1000, 0.7, 0.0, List.of(), List.of(), List.of(),
            0, 0.0, false, false);

        CalculationResult result = calculator.calculate(data);

        assertThat(result.totalCop()).isPositive();
        assertThat(result.totalUsd()).isPositive();
        assertThat(result.trmBroadspecCop()).isEqualTo(3700.0);  // 4000 - 300
        assertThat(result.usdFromTokens()).isEqualTo(50.0);       // 1000 / 20
        assertThat(result.netUsd()).isEqualTo(35.0);              // 50 * 0.7
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
    void shouldCalculateCorrectBonusTier(double tokens, double expectedBonus) {
        // Test _calculateBonusPercentage directly via reflection or package-private
    }

    @Test
    void shouldDisableFinesForHomeWorker() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.7, 0.0, List.of(), List.of(), List.of(),
            2, 0.0, false, false);  // 70%, 2 fines

        CalculationResult result = calculator.calculate(data);
        assertThat(result.showFines()).isFalse();
    }

    @Test
    void shouldEnableFinesForStudioWorker() {
        PaymentData data = new PaymentData("12345", "Test Model",
            4000.0, 4100.0, 1000, 0.6, 0.0, List.of(), List.of(), List.of(),
            2, 0.0, false, false);  // 60%, 2 fines

        CalculationResult result = calculator.calculate(data);
        assertThat(result.showFines()).isTrue();
        assertThat(result.finesTotal()).isEqualTo(60000.0);  // 2 * 30000
    }
}
```

### 15.2 `FernetCompatibilityTest.java`

```java
class FernetCompatibilityTest {
    private Path secureStoreDir;
    private Key fernetKey;

    @BeforeEach
    void setUp() throws IOException {
        // Copy test vault from resources
        secureStoreDir = Files.createTempDirectory("vault-compat-test");
        Path source = Path.of("src/test/resources/secure_store");
        // ... copy files
    }

    @Test
    @Tag("compatibility")
    void shouldDecryptExistingPythonVaultIndex() throws IOException {
        Path indexPath = secureStoreDir.resolve("vault_index.json.enc");
        byte[] enc = Files.readAllBytes(indexPath);
        Token token = Token.fromBytes(enc);
        byte[] dec = token.validateAndDecrypt(fernetKey, validator);

        String json = new String(dec, StandardCharsets.UTF_8);
        assertThat(json).contains("model_id");
        // Verify entries have expected structure
    }

    @Test
    @Tag("compatibility")
    void shouldDecryptExistingPythonVaultPdf() throws IOException {
        Path vaultPath = secureStoreDir.resolve("single_vault.zip.enc");
        byte[] enc = Files.readAllBytes(vaultPath);
        Token token = Token.fromBytes(enc);
        byte[] dec = token.validateAndDecrypt(fernetKey, validator);

        // dec should be a valid ZIP
        try (ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(dec))) {
            assertThat(zis.getNextEntry()).isNotNull();
        }
    }

    @Test
    void shouldProduceVaultReadableByPython() {
        // Write test PDF to vault using Java
        // Output instructions to verify with Python:
        //   from cryptography.fernet import Fernet
        //   f = Fernet(open('.secure_store/key.key').read())
        //   data = f.decrypt(open('single_vault.zip.enc', 'rb').read())
        //   ...
    }
}
```

### 15.3 Coverage Target

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.12</version>
    <executions>
        <execution>
            <goals><goal>prepare-agent</goal></goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals><goal>report</goal></goals>
        </execution>
        <execution>
            <id>check</id>
            <goals><goal>check</goal></goals>
            <configuration>
                <rules>
                    <rule>
                        <element>BUNDLE</element>
                        <limits>
                            <limit>
                                <counter>INSTRUCTION</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

---

## 16. CSS Styling

### `default.css` (replaces ttk style configuration)

```css
.root {
    -fx-font-family: 'Arial';
    -fx-font-size: 12px;
}

.tab-pane .tab-header-area .tab {
    -fx-font-size: 13px;
    -fx-padding: 6 16 6 16;
}

.receipt-text {
    -fx-font-family: 'Courier New', monospace;
    -fx-font-size: 11px;
    -fx-background-color: white;
}

.title-label {
    -fx-font-size: 18px;
    -fx-font-weight: bold;
    -fx-padding: 0 0 10 0;
}

.section-label {
    -fx-font-size: 12px;
    -fx-font-weight: bold;
    -fx-padding: 10 0 5 0;
}

.result-label {
    -fx-font-size: 14px;
    -fx-font-weight: bold;
    -fx-text-fill: #007bff;
}
```

---

## 17. Resolution Toggle

```java
// ResolutionManager.java
public class ResolutionManager {
    private final Stage stage;
    private final Resolution current;
    private static final Resolution RES_1920 = new Resolution(1920, 1080);
    private static final Resolution RES_1366 = new Resolution(1366, 768);
    private static final int TASKBAR_HEIGHT = 40;

    public void toggleResolution() {
        Resolution target = (current.width() == 1920) ? RES_1366 : RES_1920;
        stage.setWidth(target.width());
        stage.setHeight(target.height() - TASKBAR_HEIGHT);

        // Scale fonts and spacing
        double scale = Math.min(
            target.width() / 1920.0,
            (target.height() - TASKBAR_HEIGHT) / (1080.0 - TASKBAR_HEIGHT));

        // Apply to root node
        stage.getScene().getRoot().setStyle(
            String.format("-fx-font-size: %dpx;", Math.max(8, (int)(12 * scale))));
    }
}

record Resolution(int width, int height) {}
```

---

## 18. Build & Run Commands

```bash
# Build
mvn clean compile

# Run tests
mvn test

# Run with coverage
mvn verify

# Run application
mvn javafx:run

# Package as executable JAR
mvn package
java -jar target/PayrollUI-1.0.0.jar
```

---

## 19. Migration Checklist

### Phase 1: Foundation
- [ ] Maven project structure created
- [ ] `application.yaml` with all config keys migrated
- [ ] Data model records: `PaymentData`, `CalculationResult`, `Advance`, `OtherSite`, `VaultEntry`
- [ ] Exception hierarchy
- [ ] Utility classes: `Formatters`, `Validators`, `PdfProtocols`
- [ ] `FileOperations` with path validation and sanitization

### Phase 2: Core Services
- [ ] `PaymentCalculatorService` — all 22 FRs verified by unit tests
- [ ] `ReceiptGeneratorService` — PDFBox generation, full + model receipt
- [ ] `VaultRepository` — Fernet compatibility verified (read existing vault)
- [ ] `PdfPreviewService` — PDFBox renderer → JavaFX Image

### Phase 3: UI
- [ ] `PayrollApplication` + `MainWindow` — Stage, Scene, TabPane
- [ ] `MainTabView` — input fields, receipt display, calculation handler
- [ ] `VaultTabView` — vault list, PDF preview, crud buttons
- [ ] `AdminTabView` — COP→USD calculator
- [ ] `CalculationHandler`, `PdfSaver`, `ModelImageSaver`
- [ ] `ResolutionManager` — toggle + scaling
- [ ] CSS styling

### Phase 4: Integration & Polish
- [ ] `ApplicationController` wiring all components
- [ ] Temp file cleanup on exit
- [ ] Fernet cross-compatibility end-to-end test (Python write → Java read → Java write → Python read)
- [ ] All 22 functional requirements verified
- [ ] All 8 security requirements verified
- [ ] 80%+ code coverage

### Phase 5: Future API Project
- [ ] Split shared code (`core.model`, `core.service`, `storage`, `util`) into `payroll-common` module
- [ ] `com.broadspec.PayrollApi` depends on `payroll-common`
- [ ] `com.broadspec.PayrollUI` depends on `payroll-common`

---

## 20. File Reference Map (Python → Java)

| Python File | Java Class (package) |
|---|---|
| `broadspec/main.py:414` (main entry) | `PayrollApplication.java` |
| `broadspec/main.py:24` (ApplicationController) | `ApplicationController.java` |
| `broadspec/core/models.py:32` (PaymentData) | `PaymentData.java` (record) |
| `broadspec/core/models.py:59` (CalculationResult) | `CalculationResult.java` (@Builder) |
| `broadspec/core/models.py:7` (Advance) | `Advance.java` (record) |
| `broadspec/core/models.py:18` (OtherSite) | `OtherSite.java` (record) |
| `broadspec/core/models.py:123` (VaultEntry) | `VaultEntry.java` (record) |
| `broadspec/core/calculator.py` | `PaymentCalculatorService.java` |
| `broadspec/core/receipt_generator.py` | `ReceiptGeneratorService.java` |
| `broadspec/core/exceptions.py` | `exception/*.java` (8 classes) |
| `broadspec/ui/main_window.py:19` (BroadSpecGUI) | `MainWindow.java` |
| `broadspec/ui/components/window_setup.py` | (merged into `MainWindow.java`) |
| `broadspec/ui/components/main_tab_ui.py` | `MainTabView.java` |
| `broadspec/ui/components/vault_tab_ui.py` | `VaultTabView.java` |
| `broadspec/ui/components/admin_tab_ui.py` | `AdminTabView.java` |
| `broadspec/ui/components/calculation_handler.py` | `handler/CalculationHandler.java` |
| `broadspec/ui/components/pdf_saver.py` | `handler/PdfSaver.java` |
| `broadspec/ui/components/model_image_saver.py` | `handler/ModelImageSaver.java` |
| `broadspec/ui/components/resolution_manager.py` | `handler/ResolutionManager.java` |
| `broadspec/ui/components/pdf_preview_handler.py` | `handler/PdfPreviewHandler.java` |
| `broadspec/storage/vault_manager.py` | `VaultRepository.java` |
| `broadspec/storage/file_operations.py` | `FileOperations.java` |
| `broadspec/utils/formatters.py` | `util/Formatters.java` |
| `broadspec/utils/validators.py` | `util/Validators.java` |
| `broadspec/utils/pdf_protocols.py` | `util/PdfProtocols.java` |
| `broadspec/utils/pdf_preview.py` | `PdfPreviewService.java` |
| `config.yaml` | `src/main/resources/application.yaml` |
| `requirements/base.txt` | `pom.xml` dependencies |
| `pytest.ini` | `pom.xml` (surefire + jacoco config) |
| `conftest.py` | Test `@BeforeEach` setup methods |
| `tests/unit/test_calculator.py` | `PaymentCalculatorServiceTest.java` |
| `tests/unit/test_receipt_generator.py` | `ReceiptGeneratorServiceTest.java` |
| `tests/unit/test_vault_manager.py` | `VaultRepositoryTest.java` |
| `tests/unit/test_file_operations.py` | `FileOperationsTest.java` |
| `tests/unit/test_pdf_protocols.py` | `PdfProtocolsTest.java` |
