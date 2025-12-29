# Simulation Workflow: K8s Observability Agent

This document outlines the execution flow of the observability agent simulation (`simulate_incident.py`). The simulation validates the core logic—detection, context gathering, AI analysis, and alerting—without requiring a live Kubernetes cluster or external API credentials.

## 1. Visual Workflow (Flowchart)

```mermaid
flowchart TD
    Start([Start Simulation]) --> Setup[Setup: Mock Config & Integrations]
    Setup --> Trigger[Trigger Simulated Event: CrashLoopBackOff]
    
    subgraph Agent Core Logic
        Trigger --> Detect[Detect Failure Event]
        Detect --> Gather[Gather Context]
        
        subgraph Integrations [Parallel Data Fetching]
            Gather --> Logs[Fetch Logs (Mocked Loki)]
            Gather --> Commits[Fetch Recent Commits (Mocked GitHub)]
        end
        
        Logs & Commits --> AI[AI Risk Analysis]
        AI --> Decision{Severity Critical?}
    end
    
    subgraph Actions
        Decision -- Yes --> PagerDuty[Escalate to PagerDuty]
        Decision -- No --> SlackOnly[Slack Notification]
        PagerDuty --> Slack[Slack Notification w/ Assessment]
        SlackOnly --> Slack
    end
    
    Slack --> End([End Simulation])

    style Start fill:#f9f,stroke:#333
    style End fill:#f9f,stroke:#333
    style AI fill:#bbf,stroke:#333
    style PagerDuty fill:#ff9999,stroke:#333
    style Slack fill:#99ff99,stroke:#333
```

## 2. Detailed Explanation

### Step 1: Setup & Mocking
**File**: `simulate_incident.py`
The script begins by loading the `Agent` class but injecting "MagicMock" objects instead of real API clients.
- **Config**: Sets up dummy tokens for Slack (`xoxb-fake`), PagerDuty, and OpenAI.
- **Mocks**:
  - **Kubernetes Client**: Intercepted to prevent trying to read local kubeconfig files.
  - **Loki/Prometheus**: Returns pre-canned log entries showing a `DatabaseConnectionTimeout`.
  - **GitHub**: Returns a mocked commit diff showing a change in `db_settings.json` (host changed from `db-primary` to `db-prod-v2`).
  - **OpenAI**: Returns a fixed response: "High Risk (Score: 9/10)...".

### Step 2: Event Trigger
A simulated Kubernetes event is created manually and passed to the agent's handler.
- **Event Type**: `CrashLoopBackOff`
- **Pod**: `billing-api-7895-xyz`
- **Namespace**: `payments-billing`
- **Reason**: Container failed to start multiple times.

### Step 3: Context Gathering
The agent reacts to the event by querying its integrations to understand *why* the failure happened.
- **Logs**: It "calls" the observability client, which returns the mocked `DatabaseConnectionTimeout` error.
- **Git Diff**: It "calls" the GitHub client, which reveals that `db_settings.json` was recently modified.

### Step 4: AI Risk Analysis
The agent bundles the **Diff** and the **Logs** and sends them to the AI module.
- **Input**: "Here is the diff for commit `abcdef`. Here are the logs showing timeouts."
- **Output**: The mocked AI responds that the risk is **High (9/10)** because a config change likely broke connectivity.

### Step 5: Alerting & Escalation
Based on the event severity (`CrashLoopBackOff` is treated as critical in the code):
1.  **Slack**: A rich message is formatted. It includes the pod name, the AI's "High Risk" assessment, and the specific log error.
2.  **PagerDuty**: Because the event indicates a service crash, a PagerDuty incident is triggered (mocked print output) to wake up the on-call engineer.

## 3. Real-World Equivalence

| Simulation Step | Real-World Equivalent |
|-----------------|-----------------------|
| **Mock Event** | The `EventMonitor` `watch` loop receives a real event stream from the K8s API server using `client.CoreV1Api()`. |
| **Mock Logs** | The agent executes an HTTP GET to your Loki endpoint/Grafana instance. |
| **Mock GitHub** | The agent uses the GitHub REST API to pull the actual commit history of the deployed image tag. |
| **Mock AI** | The agent sends the text prompt to OpenAI's GPT-4 API and awaits the generation. |
| **Print Output** | Real HTTP requests are sent to Slack's Webhook URL and PagerDuty's Events API. |
