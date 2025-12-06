package com.alphora.agent101.dto;

import lombok.Data;

@Data
public class MockExecutionResult {
    private String ticketId;
    private boolean executed;
    private String message;
}
