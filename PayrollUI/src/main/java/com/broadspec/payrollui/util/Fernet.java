package com.broadspec.payrollui.util;

import javax.crypto.Cipher;
import javax.crypto.Mac;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Base64;

public final class Fernet {

    private static final byte VERSION = (byte) 0x80;
    private static final int TIMESTAMP_SIZE = 8;
    private static final int IV_SIZE = 16;
    private static final int HMAC_SIZE = 32;
    private static final int MIN_TOKEN_SIZE = 1 + TIMESTAMP_SIZE + IV_SIZE + 1 + HMAC_SIZE;

    private final byte[] signingKey;
    private final byte[] encryptionKey;

    public Fernet(byte[] rawKey) {
        if (rawKey.length != 32) {
            throw new IllegalArgumentException("Fernet key must be 32 bytes");
        }
        // cryptography >= 44: direct split (first 16 = signing, last 16 = encrypt)
        this.signingKey = Arrays.copyOfRange(rawKey, 0, 16);
        this.encryptionKey = Arrays.copyOfRange(rawKey, 16, 32);
    }

    public Fernet(String base64UrlKey) {
        this(Base64.getUrlDecoder().decode(base64UrlKey));
    }

    public static byte[] generateKey() {
        byte[] key = new byte[32];
        new java.security.SecureRandom().nextBytes(key);
        return key;
    }

    public static String encodeKey(byte[] rawKey) {
        return Base64.getUrlEncoder().withoutPadding().encodeToString(rawKey);
    }

    public byte[] decrypt(byte[] token) {
        byte[] trimmed = new String(token, java.nio.charset.StandardCharsets.UTF_8).trim()
            .getBytes(java.nio.charset.StandardCharsets.UTF_8);
        return decryptRaw(Base64.getUrlDecoder().decode(trimmed));
    }

    public byte[] decryptRaw(byte[] rawToken) {
        if (rawToken.length < MIN_TOKEN_SIZE) {
            throw new IllegalArgumentException("Token too short");
        }
        if (rawToken[0] != VERSION) {
            throw new IllegalArgumentException("Invalid version byte");
        }

        int ciphertextLen = rawToken.length - 1 - TIMESTAMP_SIZE - IV_SIZE - HMAC_SIZE;

        byte[] hmac = Arrays.copyOfRange(rawToken, rawToken.length - HMAC_SIZE, rawToken.length);
        byte[] signedData = Arrays.copyOf(rawToken, rawToken.length - HMAC_SIZE);

        byte[] computedHmac = hmacSha256(signingKey, signedData);
        if (!MessageDigest.isEqual(computedHmac, hmac)) {
            throw new IllegalArgumentException("HMAC verification failed");
        }

        byte[] iv = Arrays.copyOfRange(rawToken, 1 + TIMESTAMP_SIZE, 1 + TIMESTAMP_SIZE + IV_SIZE);
        byte[] ciphertext = Arrays.copyOfRange(rawToken, 1 + TIMESTAMP_SIZE + IV_SIZE,
            1 + TIMESTAMP_SIZE + IV_SIZE + ciphertextLen);

        try {
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            cipher.init(Cipher.DECRYPT_MODE,
                new SecretKeySpec(encryptionKey, "AES"),
                new IvParameterSpec(iv));
            return cipher.doFinal(ciphertext);
        } catch (Exception e) {
            throw new IllegalArgumentException("Decryption failed: " + e.getMessage(), e);
        }
    }

    public byte[] encrypt(byte[] plaintext) {
        return Base64.getUrlEncoder().withoutPadding().encode(encryptRaw(plaintext));
    }

    public byte[] encryptRaw(byte[] plaintext) {
        long timestamp = System.currentTimeMillis() / 1000;
        byte[] iv = new byte[IV_SIZE];
        new java.security.SecureRandom().nextBytes(iv);

        byte[] ciphertext;
        try {
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE,
                new SecretKeySpec(encryptionKey, "AES"),
                new IvParameterSpec(iv));
            ciphertext = cipher.doFinal(plaintext);
        } catch (Exception e) {
            throw new IllegalArgumentException("Encryption failed: " + e.getMessage(), e);
        }

        ByteBuffer signedData = ByteBuffer.allocate(1 + TIMESTAMP_SIZE + IV_SIZE + ciphertext.length);
        signedData.put(VERSION);
        signedData.putLong(timestamp);
        signedData.put(iv);
        signedData.put(ciphertext);

        byte[] signedBytes = signedData.array();
        byte[] hmac = hmacSha256(signingKey, signedBytes);

        ByteBuffer token = ByteBuffer.allocate(signedBytes.length + HMAC_SIZE);
        token.put(signedBytes);
        token.put(hmac);
        return token.array();
    }

    private static byte[] hmacSha256(byte[] key, byte[] data) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(key, "HmacSHA256"));
            return mac.doFinal(data);
        } catch (Exception e) {
            throw new RuntimeException("HMAC-SHA256 failed", e);
        }
    }
}
