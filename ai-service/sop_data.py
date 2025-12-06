SOPS = {
    "PASSWORD_RESET": [
        "Verify requester identity via email",
        "Reset password in IdP",
        "Force password change on next login",
        "Notify user with temporary password"
    ],
    "PRINTER_ISSUE": [
        "Ask user to confirm printer name and location",
        "Restart print spooler service",
        "Print test page",
        "If still failing, escalate to L2"
    ],
    "VPN_ACCESS": [
        "Verify user is allowed VPN access",
        "Create / update VPN profile in system",
        "Send connection instructions to user"
    ]
}
