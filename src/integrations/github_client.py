import requests
from ..config import GitHubConfig
from ..logger import get_logger

logger = get_logger(__name__)

class GitHubClient:
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.config.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_recent_commits(self, limit: int = 5):
        if not self.config.enabled:
            logger.info("GitHub integration disabled")
            return []
            
        url = f"{self.base_url}/repos/{self.config.repo_owner}/{self.config.repo_name}/commits"
        try:
            response = requests.get(url, headers=self.headers, params={"per_page": limit})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to fetch commits", error=str(e))
            return []

    def get_commit_diff(self, commit_sha: str):
        if not self.config.enabled:
            return None
            
        url = f"{self.base_url}/repos/{self.config.repo_owner}/{self.config.repo_name}/commits/{commit_sha}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('files', [])
        except Exception as e:
            logger.error("Failed to fetch commit diff", sha=commit_sha, error=str(e))
            return []
