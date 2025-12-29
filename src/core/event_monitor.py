from kubernetes import client, config, watch
from ..logger import get_logger
import time

logger = get_logger(__name__)

class EventMonitor:
    def __init__(self):
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException:
                logger.warning("Could not load Kube config. Kubernetes monitoring will fail.")
                self.v1 = None
                return

        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()

    def watch_events(self, callback):
        if not self.v1:
            return

        w = watch.Watch()
        logger.info("Starting K8s Event Watcher...")
        
        # In a real agent, this loop should be robust against disconnections
        for event in w.stream(self.v1.list_event_for_all_namespaces):
            obj = event['object']
            # Simple heuristic for failure: type is warning and reason indicates failure
            if obj.type == "Warning" and obj.reason in ["Failed", "BackOff", "Unhealthy", "FailedScheduling"]:
                logger.info("Detected K8s Warning Event", reason=obj.reason, message=obj.message)
                
                # Transform to an internal event structure
                incident_event = {
                    "type": "k8s_failure",
                    "namespace": obj.metadata.namespace,
                    "pod_name": obj.involved_object.name,
                    "reason": obj.reason,
                    "message": obj.message,
                    "timestamp": obj.last_timestamp
                }
                callback(incident_event)

    def simulate_mcp_event(self, event_data, callback):
        # Allow manual injection for testing
        callback(event_data)
