package com.alphora.agent101.dto;

import lombok.Data;

import java.util.List;

@Data
public class ActionPlanDto {
    private String ticketId;
    private String intent;
    private String decision;            // AUTO_RESOLVE / REQUIRE_APPROVAL / ESCALATE
    private List<String> steps;
}
