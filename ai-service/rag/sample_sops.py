"""
Sample SOPs for testing and demonstration
These would normally be loaded from client documentation
"""

from typing import List, Dict

SAMPLE_SOPS = [
    {
        "tenant_id": "tenant1",
        "title": "Password Reset Procedure",
        "category": "password_reset",
        "tags": ["authentication", "security", "user_management"],
        "content": """
Password Reset Standard Operating Procedure

Purpose: This procedure outlines the steps to safely reset user passwords for employees who have forgotten their credentials or are locked out of their accounts.

Prerequisites:
- Verify user identity through secondary authentication (email or phone)
- Confirm the user is authorized in the company directory
- Check if the account is not under security review or suspended

Step 1: Identity Verification
Contact the user through their registered email or phone number. Ask them to provide:
- Full name
- Employee ID or username
- Department
- Manager name
Never reset a password without proper verification.

Step 2: Check Account Status
Log into the Active Directory or identity provider console. Verify that:
- The account exists and is active
- The account is not locked due to security violations
- The user has the appropriate permissions for their role

Step 3: Generate Temporary Password
Use the identity provider's password generation tool to create a secure temporary password that meets these requirements:
- Minimum 12 characters
- Contains uppercase, lowercase, numbers, and special characters
- Does not match any of the user's previous 5 passwords

Step 4: Reset Password
In the identity management console:
1. Navigate to the user's account
2. Select "Reset Password"
3. Enter the temporary password
4. Check the box "User must change password at next login"
5. If available, set password expiration to 24 hours

Step 5: Communicate New Password
Send the temporary password to the user through a secure channel:
- Use company's secure messaging system if available
- Otherwise, call the user and read the password over the phone
- Never send passwords via unencrypted email

Step 6: Verify Successful Login
Ask the user to:
1. Log in with the temporary password
2. Set their new permanent password
3. Confirm they can access their required systems

Step 7: Documentation
Log the following in the ticketing system:
- Date and time of reset
- User verified and method of verification
- Temporary password expiration time
- Confirmation of successful password change
- Total time spent: typically 10-15 minutes

Common Issues:
- If user cannot receive the password: arrange for in-person verification
- If account is locked: check for recent failed login attempts
- If password policy prevents reset: escalate to IT security team

Security Notes:
- All password resets must be logged for audit purposes
- Suspicious reset requests should be escalated immediately
- Users who frequently request resets may need additional security training
        """,
        "metadata": {
            "version": "2.1",
            "last_updated": "2024-11-15",
            "approval_required": False,
            "estimated_time_minutes": 15
        }
    },
    {
        "tenant_id": "tenant1",
        "title": "System Restart Procedure",
        "category": "system_restart",
        "tags": ["maintenance", "troubleshooting", "performance"],
        "content": """
System Restart Standard Operating Procedure

Purpose: This procedure describes how to safely restart Windows and Linux servers and workstations to resolve performance issues, apply updates, or complete software installations.

When to Use:
- System is running slowly or unresponsive
- After installing updates that require a restart
- Application crashes or freezes persist
- Memory usage is abnormally high
- As part of scheduled maintenance

Prerequisites:
- Verify no critical processes are running
- Check for active user sessions
- Confirm a maintenance window is scheduled for servers
- Notify affected users at least 15 minutes in advance

Step 1: Assessment
Before restarting, determine:
- Is this a workstation or server?
- Are there any active users or critical services?
- Is this restart urgent or can it be scheduled?
- What is the expected downtime?

For servers: Always check with the application owner first.

Step 2: Pre-Restart Checks
Log into the RMM (Remote Monitoring and Management) tool and verify:
- Current system uptime
- Running processes and services
- Recent system logs for errors
- Available disk space (should be above 10%)
- Backup status (last backup should be within 24 hours)

Step 3: User Notification (for workstations)
If the user is logged in:
1. Send a pop-up notification through RMM: "Your computer needs to restart for maintenance. Please save your work. Restart will occur in 15 minutes."
2. Wait for user confirmation or 15 minutes to elapse
3. If urgent, contact user by phone or email

Step 4: Save System State
Before restarting:
- Document currently running services
- Note any custom applications that may not auto-start
- Screenshot any error messages being addressed
- Save the system event log for the past 24 hours

Step 5: Initiate Restart
For Windows Systems:
1. Open RMM remote shell
2. Execute: shutdown /r /t 60 /c "System restart for maintenance"
3. Monitor the restart progress through RMM

For Linux Systems:
1. SSH into the system through RMM
2. Execute: sudo shutdown -r +1 "System restart for maintenance"
3. Monitor through RMM console

Step 6: Post-Restart Verification
After the system comes back online (typically 3-5 minutes):
- Verify system is accessible via RMM
- Check that all critical services have started
- For servers: verify applications are responding
- Review system logs for any startup errors
- Test user access and functionality

Step 7: Documentation
Update the ticket with:
- Restart reason and time
- Pre-restart system state
- Post-restart verification results
- Any services that failed to start
- User confirmation that issue is resolved
- Total downtime duration

Step 8: Follow-up
If the restart was for troubleshooting:
- Monitor system for 24 hours
- Check if the original issue persists
- Schedule follow-up if needed
- Consider deeper investigation if problems continue

Rollback Procedure:
If the system fails to start properly:
1. Attempt safe mode boot
2. Review system logs for boot failures
3. If server: fail over to backup if available
4. Escalate to senior technician if system does not recover within 15 minutes

Common Issues:
- System stuck in boot loop: escalate immediately
- Services fail to start: check dependencies and restart manually
- User unable to log in: verify network connectivity and authentication services
- Performance still poor: may need deeper troubleshooting beyond restart

Safety Notes:
- Never restart production servers during business hours without approval
- Always verify backup status before restarting servers
- Document everything for compliance and audit purposes
        """,
        "metadata": {
            "version": "1.8",
            "last_updated": "2024-10-30",
            "approval_required": True,
            "estimated_time_minutes": 20
        }
    },
    {
        "tenant_id": "tenant1",
        "title": "VPN Access Setup",
        "category": "vpn_access",
        "tags": ["remote_access", "security", "networking"],
        "content": """
VPN Access Setup Standard Operating Procedure

Purpose: This procedure details how to provision and configure VPN access for employees who need to connect to the corporate network remotely.

Prerequisites:
- User must be an active employee with valid account
- Manager approval required for new VPN access
- User's device must meet minimum security requirements
- User must have completed security awareness training

Step 1: Request Validation
Verify the following in the ticket:
- User's full name and employee ID
- Manager approval (attached or referenced)
- Business justification for VPN access
- Expected duration (temporary or permanent)
- Device type (Windows, Mac, Linux, mobile)

Step 2: Security Compliance Check
Before provisioning access, verify:
- User's account is in good standing
- No recent security incidents associated with user
- Device meets company security policy:
  * Updated operating system (within 2 versions of current)
  * Antivirus installed and active
  * Full disk encryption enabled
  * Firewall active

Step 3: VPN Profile Creation
Log into the VPN management console (FortiClient, Cisco AnyConnect, or equivalent):

For new users:
1. Navigate to User Management
2. Click "Add New VPN User"
3. Enter user details:
   - Username: use company email format
   - Authentication: set to MFA required
   - Group: assign to appropriate VPN group based on department
   - Bandwidth: set to standard (50 Mbps) unless otherwise approved
4. Generate user credentials
5. Set VPN profile expiration if temporary access

For existing users needing reactivation:
1. Locate user profile
2. Verify credentials are current
3. Update expiration date if needed
4. Reset MFA if required

Step 4: Multi-Factor Authentication Setup
Configure MFA for the VPN account:
1. Register user's mobile device or hardware token
2. Send MFA enrollment link to user's email
3. Verify user completes enrollment within 24 hours
4. Test MFA functionality before providing VPN credentials

Step 5: Client Software Deployment
Prepare VPN client installation:

For company-managed devices:
- Deploy client via RMM or software distribution tool
- Configuration profile pushed automatically

For BYOD (Bring Your Own Device):
- Send download link to official VPN client
- Include step-by-step installation guide
- Provide company-specific configuration file
- Include troubleshooting guide

Step 6: User Communication
Send welcome email to user containing:
- VPN client download link (if not auto-deployed)
- Connection server address
- Username and temporary password
- MFA setup instructions
- Quick start guide
- IT support contact information
- Security reminders:
  * Never share VPN credentials
  * Always lock screen when away
  * Report suspicious activity immediately

Step 7: Connection Testing
Schedule a test call with the user:
1. Guide them through first connection
2. Verify they can authenticate successfully
3. Test access to required internal resources:
   - File shares
   - Internal applications
   - Email and collaboration tools
4. Confirm connection speed is adequate
5. Ensure auto-disconnect works after idle timeout

Step 8: Documentation and Monitoring
In the ticketing system, document:
- Date and time VPN access was granted
- VPN group assignment
- Expiration date (if applicable)
- MFA method configured
- Test results and user confirmation

Set up monitoring:
- Add user to VPN access review list
- Schedule periodic access review (every 90 days)
- Enable alerts for suspicious connection patterns

Step 9: Ongoing Support
Inform user about common issues:
- Connection drops: check internet stability, try different network
- Authentication fails: verify password, check MFA device
- Slow performance: may be bandwidth issue, disconnect and reconnect
- Access denied errors: contact IT to verify permissions

Provide escalation path for unresolved issues.

Revocation Procedure:
When user leaves company or no longer needs access:
1. Disable VPN account within 24 hours
2. Remove from all VPN groups
3. Revoke MFA registrations
4. Update documentation
5. Verify account cannot authenticate

Security Considerations:
- Monitor failed login attempts (3+ failures trigger review)
- Review VPN logs weekly for anomalies
- Enforce strong password policy (12+ characters, complexity)
- Require VPN client updates within 30 days of release
- Conduct quarterly access reviews with department managers

Compliance Notes:
- All VPN access must be approved and documented
- Access logs retained for minimum 1 year
- Failed access attempts investigated within 24 hours
- Quarterly access reviews mandatory for compliance
        """,
        "metadata": {
            "version": "2.0",
            "last_updated": "2024-12-01",
            "approval_required": True,
            "estimated_time_minutes": 30
        }
    },
    {
        "tenant_id": "tenant1",
        "title": "Backup Verification Procedure",
        "category": "backup_verification",
        "tags": ["data_protection", "disaster_recovery", "maintenance"],
        "content": """
Backup Verification Standard Operating Procedure

Purpose: This procedure ensures that backup jobs are completing successfully and data can be restored if needed.

Step 1: Access Backup Management Console
Log into the backup software (Veeam, Acronis, or company-specific solution).

Step 2: Check Backup Job Status
Review the last 24 hours of backup jobs:
- Identify any failed or incomplete jobs
- Check warning messages
- Verify all systems were included in backup window

Step 3: Verify Backup Integrity
For each critical system:
- Check backup file size (should be consistent with expectations)
- Verify backup completed within the allocated time window
- Review logs for any errors or warnings
- Confirm backup was transferred to offsite/cloud storage

Step 4: Test Restore (Monthly)
At least monthly, perform test restores:
- Select a random file from backup
- Restore to test environment
- Verify file integrity and accessibility
- Document test results

Step 5: Report Issues
If any backups failed:
- Investigate root cause (disk space, network, permissions)
- Re-run failed backup jobs
- Escalate persistent failures to senior engineer
- Update disaster recovery team

Step 6: Documentation
Record verification in the ticketing system:
- Date and time of verification
- Jobs checked and their status
- Any issues found and resolution
- Test restore results if performed
        """,
        "metadata": {
            "version": "1.5",
            "last_updated": "2024-09-20",
            "approval_required": False,
            "estimated_time_minutes": 15
        }
    }
]


def get_sample_sops(tenant_id: str = "tenant1") -> List[Dict]:
    """
    Get sample SOPs for a specific tenant.

    Args:
        tenant_id: Tenant identifier

    Returns:
        List of SOP dictionaries ready for ingestion
    """
    return [sop for sop in SAMPLE_SOPS if sop['tenant_id'] == tenant_id]


def get_all_sample_sops() -> List[Dict]:
    """Get all sample SOPs across all tenants."""
    return SAMPLE_SOPS