from pdpyras import APISession, PDClientError
from ..config import PagerDutyConfig
from ..logger import get_logger

logger = get_logger(__name__)

class PagerDutyClient:
    def __init__(self, config: PagerDutyConfig):
        self.config = config
        self.session = APISession(self.config.api_key) if config.enabled else None

    def create_incident(self, title: str, details: str):
        if not self.config.enabled:
            logger.info("PagerDuty disabled, skipping incident", title=title)
            return

        try:
            # This is a simplified call; real PD integration often uses the Events API v2 for firing alerts
            # But here we use the REST API to create an incident directly on a service
            payload = {
                "incident": {
                    "type": "incident",
                    "title": title,
                    "service": {
                        "id": self.config.service_id,
                        "type": "service_reference"
                    },
                    "body": {
                        "type": "incident_body",
                        "details": details
                    }
                }
            }
            return self.session.rpost("incidents", json=payload)
        except PDClientError as e:
            logger.error("Failed to create PagerDuty incident", error=str(e))
