import time
import threading
from ..config import AppConfig
from ..logger import get_logger
from .event_monitor import EventMonitor
from ..integrations.github_client import GitHubClient
from ..integrations.slack_client import SlackClient
from ..integrations.pagerduty_client import PagerDutyClient
from ..integrations.observability import ObservabilityClient
from ..ai.risk_analyzer import RiskAnalyzer
from ..remediation.strategies import RemediationEngine

logger = get_logger(__name__)

class Agent:
    def __init__(self, config: AppConfig):
        self.config = config
        self.monitor = EventMonitor()
        self.github = GitHubClient(config.github)
        self.slack = SlackClient(config.slack)
        self.pd = PagerDutyClient(config.pagerduty)
        self.obs = ObservabilityClient(config.observability)
        self.ai = RiskAnalyzer(config.ai)
        self.remediation = RemediationEngine()

    def handle_incident(self, event):
        logger.info("Handling Incident", incident_event=event)
        
        # 1. Gather Context
        namespace = event.get('namespace')
        pod = event.get('pod_name')
        
        # Fetch Logs
        logs = self.obs.get_logs(f'{{pod="{pod}"}}')
        log_str = "\n".join([l['values'][0][1] for l in logs]) if logs else "No logs found."

        # Fetch Commits (Simplified assumption: service name maps to repo)
        commits = self.github.get_recent_commits()
        latest_commit_sha = commits[0]['sha'] if commits else None
        diff = self.github.get_commit_diff(latest_commit_sha) if latest_commit_sha else []
        diff_str = str(diff)

        # 2. AI Analysis
        risk_analysis = self.ai.analyze_risk(diff_str, log_str)

        # 3. Notify Slack
        message = f"""
        *Incident Detected*: {event.get('message')}
        *Namespace*: {namespace}
        *Pod*: {pod}
        *AI Analysis*: {risk_analysis}
        
        <http://grafana/d/xyz|Grafana Dashboard>
        """
        self.slack.send_alert("Deployment Failure", message, severity="high", incident_id=f"{namespace}-{pod}")

        # 4. Escalate to PagerDuty if critical (mock logic)
        if "CrashLoopBackOff" in event.get('reason', ''):
            self.pd.create_incident(f"Critical: {pod} CrashLoopBackOff", message)

    def start(self):
        logger.info("Agent starting...")
        # Start event loop in a separate thread so main can handle healthchecks or stay alive
        t = threading.Thread(target=self.monitor.watch_events, args=(self.handle_incident,))
        t.daemon = True
        t.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping agent...")
