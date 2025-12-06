package com.alphora.agent101.dto;

import lombok.Data;

@Data
public class ClassificationResult {
    private String intent;          // "PASSWORD_RESET", "PRINTER_ISSUE", "VPN_ACCESS"
    private String riskLevel;       // "LOW", "MEDIUM", "HIGH"
    private double confidence;      // 0.0 - 1.0
}

