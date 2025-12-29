# K8s Observability & Automation Agent

A production-grade Kubernetes agent designed to detect deployment failures, analyze root causes using AI, and automate incident response across GitHub, Slack, and PagerDuty.

## Features

- **Failure Detection**: Real-time monitoring of Kubernetes events (Pod failures, CrashLoopBackOff).
- **AI-Powered Analysis**: Uses OpenAI to analyze commit diffs and logs to predict risk and suggest fixes.
- **Multi-Channel Alerts**: Rich notifications in Slack (with buttons) and critical escalations in PagerDuty.
- **Observability Integration**: Fetches metrics (Prometheus), logs (Loki), and snapshots (Grafana) for context.
- **Automated Remediation**: Can trigger rollbacks (via simulation in this version) for unstable deployments.

## Project Structure

```
k8s-observability-agent/
├── src/                # Source code
│   ├── core/           # Main agent loop and event monitor
│   ├── integrations/   # Clients for Slack, GitHub, PD, Prom/Loki
│   ├── ai/             # AI logic
│   └── remediation/    # Rollback strategies
├── helm/               # Helm chart for K8s deployment
├── Dockerfile          # Container definition
└── config.yaml.example # Configuration reference
```

## Setup & Usage

### Prerequisites

- Python 3.11+
- Kubernetes Cluster
- OpenAI API Key (optional)
- Slack Bot Token (optional)

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure:
   Copy `config.yaml.example` to `config.yaml` and fill in your credentials.

3. Run:
   ```bash
   python -m src.main
   ```

### Docker Build

```bash
docker build -t k8s-observability-agent .
```

### Kubernetes Deployment (Helm)

1. Update `helm/values.yaml` with your secrets and config.
2. Install:
   ```bash
   helm install monitor ./helm
   ```

## Architecture

The agent runs as a Deployment in your cluster. It watches the Kubernetes Event API. When a failure event is detected:
1. It aggregates logs from Loki and metrics from Prometheus.
2. It fetches the latest commit changes from GitHub.
3. It sends this context to the AI module for analysis.
4. It dispatches a rich alert to Slack.
5. If critical, it triggers a PagerDuty incident.
