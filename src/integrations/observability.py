import requests
from prometheus_api_client import PrometheusConnect
from ..config import ObservabilityConfig
from ..logger import get_logger

logger = get_logger(__name__)

class ObservabilityClient:
    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.prom = PrometheusConnect(url=config.prometheus_url, disable_ssl=True)
    
    def get_metrics(self, query: str):
        try:
            return self.prom.custom_query(query=query)
        except Exception as e:
            logger.error("Prometheus query failed", error=str(e))
            return []

    def get_logs(self, query: str, limit: int = 100):
        # Basic Loki query via HTTP API
        url = f"{self.config.loki_url}/loki/api/v1/query_range"
        params = {"query": query, "limit": limit}
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            return resp.json().get('data', {}).get('result', [])
        except Exception as e:
            logger.error("Loki query failed", error=str(e))
            return []

    def get_grafana_snapshot(self, dashboard_uid: str):
        # Create a snapshot
        url = f"{self.config.grafana_url}/api/snapshots"
        headers = {"Authorization": f"Bearer {self.config.grafana_token}"}
        payload = {
            "dashboardId": 0, # Should rely on other means or just generic snapshot
            "expires": 3600
        }
        try:
            resp = requests.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json().get('url')
        except Exception as e:
            logger.error("Grafana snapshot failed", error=str(e))
            return None
