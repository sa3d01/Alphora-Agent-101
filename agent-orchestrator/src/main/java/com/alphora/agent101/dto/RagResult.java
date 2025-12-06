package com.alphora.agent101.dto;

import lombok.Data;

import java.util.List;

@Data
public class RagResult {
    private String tenantId;
    private String intent;
    private List<String> sopSteps;      // Plain steps for MVP
}
