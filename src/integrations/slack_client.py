from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from ..config import SlackConfig
from ..logger import get_logger

logger = get_logger(__name__)

class SlackClient:
    def __init__(self, config: SlackConfig):
        self.config = config
        self.client = WebClient(token=self.config.token) if config.enabled else None

    def send_alert(self, title: str, message: str, severity: str = "info", incident_id: str = None):
        if not self.config.enabled:
            logger.info("Slack disabled, skipping alert", title=title)
            return

        color = "#36a64f" if severity == "info" else "#ff0000"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 {title}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]
        
        if incident_id:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Acknowledge"
                        },
                        "style": "primary",
                        "value": f"ack_{incident_id}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Rollback"
                        },
                        "style": "danger",
                        "value": f"rollback_{incident_id}"
                    }
                ]
            })

        try:
            self.client.chat_postMessage(
                channel=self.config.channel,
                blocks=blocks,
                text=title 
            )
        except SlackApiError as e:
            logger.error("Failed to send Slack message", error=e.response["error"])
