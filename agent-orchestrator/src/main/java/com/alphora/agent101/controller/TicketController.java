package com.alphora.agent101.controller;

import com.alphora.agent101.dto.ActionPlanDto;
import com.alphora.agent101.dto.IncomingTicketDto;
import com.alphora.agent101.dto.MockExecutionResult;
import com.alphora.agent101.service.OrchestratorService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/tickets")
@RequiredArgsConstructor
public class TicketController {

    private final OrchestratorService orchestratorService;

    @PostMapping("/simulate")
    public ActionPlanDto simulate(@RequestBody IncomingTicketDto ticket) {
        return orchestratorService.handleTicket(ticket);
    }

    @PostMapping("/simulate/execute")
    public MockExecutionResult simulateAndExecute(@RequestBody IncomingTicketDto ticket) {
        ActionPlanDto plan = orchestratorService.handleTicket(ticket);
        return orchestratorService.executeMock(plan);
    }
}
