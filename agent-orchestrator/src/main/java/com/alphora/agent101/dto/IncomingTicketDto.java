package com.alphora.agent101.dto;

import lombok.Data;

@Data
public class IncomingTicketDto {
    private String ticketId;
    private String tenantId;
    private String subject;
    private String description;
    private String requesterEmail;
}
