package com.alphora.agent101.service;

import com.alphora.agent101.dto.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
@RequiredArgsConstructor
public class OrchestratorService {

    private final WebClient aiClient = WebClient.create("http://localhost:8000");

    public ActionPlanDto handleTicket(IncomingTicketDto ticket) {

        ClassificationResult classification = aiClient.post()
                .uri("/classify")
                .bodyValue(ticket)
                .retrieve()
                .bodyToMono(ClassificationResult.class)
                .block();

        RagResult ragResult = aiClient.post()
                .uri("/rag")
                .bodyValue(ticket)
                .retrieve()
                .bodyToMono(RagResult.class)
                .block();

        ActionPlanDto plan = aiClient.post()
                .uri("/plan")
                .bodyValue(new PlanRequest(ticket.getTicketId(), classification, ragResult))
                .retrieve()
                .bodyToMono(ActionPlanDto.class)
                .block();

        // Simple safety gate: low risk + confidence > 0.8 => auto
        if ("LOW".equalsIgnoreCase(classification.getRiskLevel())
                && classification.getConfidence() >= 0.8) {
            plan.setDecision("AUTO_RESOLVE");
        } else if ("HIGH".equalsIgnoreCase(classification.getRiskLevel())
                || classification.getConfidence() < 0.6) {
            plan.setDecision("ESCALATE");
        } else {
            plan.setDecision("REQUIRE_APPROVAL");
        }

        return plan;
    }

    public MockExecutionResult executeMock(ActionPlanDto plan) {
        // for MVP: just simulate execution instead of real tools
        MockExecutionResult result = new MockExecutionResult();
        result.setTicketId(plan.getTicketId());

        if (!"AUTO_RESOLVE".equals(plan.getDecision())) {
            result.setExecuted(false);
            result.setMessage("Execution skipped - decision = " + plan.getDecision());
            return result;
        }

        // Call AI service mock executor to simulate tool usage
        aiClient.post()
                .uri("/execute-mock")
                .bodyValue(plan)
                .retrieve()
                .bodyToMono(Void.class)
                .block();

        result.setExecuted(true);
        result.setMessage("Mock actions executed successfully for ticket " + plan.getTicketId());
        return result;
    }
}
