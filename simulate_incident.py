import sys
import os
import time
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'k8s-observability-agent'))

# Mock libraries that might not be configured or reachable
sys.modules['kubernetes'] = MagicMock()
sys.modules['kubernetes.client'] = MagicMock()
sys.modules['kubernetes.config'] = MagicMock()
sys.modules['kubernetes.watch'] = MagicMock()
sys.modules['openai'] = MagicMock()

# Now we can safely import our code
from src.core.agent import Agent
from src.config import AppConfig, SlackConfig, PagerDutyConfig, ObservabilityConfig, AIConfig
from src.logger import setup_logging

def run_simulation():
    print("🚀 Starting K8s Observability Agent Simulation...\n")
    setup_logging("INFO")

    # 1. Setup Configuration
    config = AppConfig(
        service_name="sim-agent",
        slack=SlackConfig(enabled=True, token="fake", channel="#alerts"),
        pagerduty=PagerDutyConfig(enabled=True, api_key="fake", service_id="SVC123"),
        ai=AIConfig(enabled=True, openai_api_key="fake"),
        observability=ObservabilityConfig()
    )

    # 2. Initialize Agent
    agent = Agent(config)

    # 3. Patch the integrations to simulate external services
    print("🔧 Mocking external integrations (GitHub, OpenAI, Prometheus, Slack)...\n")
    
    # Mock Observability (Logs)
    agent.obs.get_logs = MagicMock(return_value=[
        {'values': [[0, 'ERROR: DatabaseConnectionTimeout: Could not connect to db-primary:5432']]},
        {'values': [[0, 'FATAL: Application startup failed due to configuration error']]}
    ])
    
    # Mock GitHub (Commits)
    agent.github.get_recent_commits = MagicMock(return_value=[{'sha': 'abcdef123'}])
    agent.github.get_commit_diff = MagicMock(return_value=[
        {'filename': 'config/db_settings.json', 'status': 'modified', 'patch': '@@ -12,3 +12,3 @@\n- "host": "db-primary"\n+ "host": "db-prod-v2"'}
    ])

    # Mock AI
    agent.ai.analyze_risk = MagicMock(return_value="🔥 High Risk (Score: 9/10). The commit 'abcdef123' modified `db_settings.json` changing the database host. The logs show connection timeouts, indicating the new host is unreachable or firewalled.")

    # Mock Slack & PagerDuty outputs
    agent.slack.send_alert = MagicMock(side_effect=lambda title, msg, **kwargs: print(f"\n[SLACK NOTIFICATION]\nChannel: #alerts\nTitle: {title}\nMessage: {msg}\n" + "-"*50))
    agent.pd.create_incident = MagicMock(side_effect=lambda title, details: print(f"\n[PAGERDUTY ESCALATION]\nService: SVC123\nTitle: {title}\nDetails: {details}\n" + "="*50))

    # 4. Create a simulated failure event
    failure_event = {
        "namespace": "payments-billing",
        "pod_name": "billing-api-7895-xyz",
        "reason": "CrashLoopBackOff",
        "message": "Back-off restarting failed container",
        "timestamp": "2023-12-30T10:00:00Z"
    }

    print(f"⚡ SIMULATING FAILURE EVENT: {failure_event['reason']} on {failure_event['pod_name']}")
    time.sleep(1)

    # 5. Trigger the handler
    agent.handle_incident(failure_event)

    print("\n✅ Simulation Complete.")

if __name__ == "__main__":
    run_simulation()
