from openai import OpenAI
from ..config import AIConfig
from ..logger import get_logger

logger = get_logger(__name__)

class RiskAnalyzer:
    def __init__(self, config: AIConfig):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key) if config.enabled else None

    def analyze_risk(self, commit_diff: str, logs: str) -> str:
        if not self.config.enabled:
            return "AI Analysis Disabled"

        prompt = f"""
        Analyze the following deployment failure context for risk and root cause.
        
        Commit Diff Summary:
        {commit_diff[:1000]}...

        Recent Logs:
        {logs[:1000]}...
        
        Provide a short summary of the likely cause and a risk score (1-10).
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("AI analysis failed", error=str(e))
            return "AI Analysis Failed"
