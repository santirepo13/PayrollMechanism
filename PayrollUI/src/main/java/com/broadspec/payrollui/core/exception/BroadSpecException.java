package com.broadspec.payrollui.core.exception;

public class BroadSpecException extends RuntimeException {
    public BroadSpecException(String message) { super(message); }
    public BroadSpecException(String message, Throwable cause) { super(message, cause); }
}
