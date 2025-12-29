import os
import yaml
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class SlackConfig(BaseModel):
    token: str = Field(default="")
    channel: str = Field(default="#alerts")
    enabled: bool = False

class PagerDutyConfig(BaseModel):
    api_key: str = Field(default="")
    service_id: str = Field(default="")
    enabled: bool = False

class GitHubConfig(BaseModel):
    token: str = Field(default="")
    repo_owner: str = Field(default="")
    repo_name: str = Field(default="")
    enabled: bool = False

class ObservabilityConfig(BaseModel):
    prometheus_url: str = "http://prometheus-server"
    loki_url: str = "http://loki"
    grafana_url: str = "http://grafana"
    grafana_token: str = ""

class AIConfig(BaseModel):
    openai_api_key: str = Field(default="")
    model: str = "gpt-4-turbo"
    enabled: bool = False

class AppConfig(BaseModel):
    service_name: str = "k8s-observability-agent"
    log_level: str = "INFO"
    slack: SlackConfig = Field(default_factory=SlackConfig)
    pagerduty: PagerDutyConfig = Field(default_factory=PagerDutyConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    ai: AIConfig = Field(default_factory=AIConfig)

def load_config(path: str = "config.yaml") -> AppConfig:
    config_data = {}
    
    # Load from YAML if exists
    if os.path.exists(path):
        with open(path, 'r') as f:
            config_data = yaml.safe_load(f) or {}

    # Override with Environment Variables (simple mapping for key props)
    if os.getenv("SLACK_TOKEN"):
        config_data.setdefault('slack', {})['token'] = os.environ["SLACK_TOKEN"]
    if os.getenv("OPENAI_API_KEY"):
        config_data.setdefault('ai', {})['openai_api_key'] = os.environ["OPENAI_API_KEY"]
    
    return AppConfig(**config_data)
