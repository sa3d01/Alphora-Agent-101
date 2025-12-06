package com.alphora.agent101.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class PlanRequest {
    private String ticketId;
    private ClassificationResult classification;
    private RagResult ragResult;
}
