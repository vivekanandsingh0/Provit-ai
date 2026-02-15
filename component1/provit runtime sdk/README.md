# ProVit AI Runtime SDK (v0)

A lightweight, non-blocking Python SDK for capturing AI runtime evidence. Designed for high-assurance environments where model decisions must be auditable without impacting inference latency.

## Features
- **Fire-and-Forget:** Minimal latency overhead (<1ms typical).
- **Fail-Safe:** Never crashes the host application; network errors are silently suppressed.
- **Zero Dependencies:** Uses only the Python standard library.
- **Thread-Safe:** Dispatches events asynchronously on a daemon thread.

## Installation

### From Source (Development)
```bash
cd component1
pip install -e .
```

### Usage

```python
from provit_sdk import ProVitClient

# 1. Initialize the Client
client = ProVitClient(
    api_key="your-api-key",
    api_url="https://api.provit.ai", # Or your internal endpoint
    debug=True # Set to False in production to suppress error logs
)

# 2. Capture Evidence (Non-blocking)
client.ai_runtime(
    decision_id="txn-123456",
    model_name="fraud_detection_model",
    model_version="v1.0.0",
    label="approve",
    confidence_score=0.98
)
```

## Development & Testing

This repository includes a mock server and test suite to verify integration without hitting the real ProVit API.

### 1. Run the Mock Server
Start the server in one terminal window. It mimics the ProVit ingestion endpoint on `http://localhost:8080`.

```bash
python mock_provit_server.py
```

### 2. Run the Example Script
In a separate terminal, run the usage example. You should see the evidence appear in the server logs.

```bash
python example_usage.py
```

### 3. Run Unit Tests
Execute the self-contained test suite, which verifies threading, fail-safe behavior, and data formatting.

```bash
python test_provit_sdk.py
```

## Evidence Structure
The SDK emits events in the following canonical JSON format:

```json
{
  "event_type": "ai.runtime",
  "decision_id": "txn-123456",
  "timestamp": "2026-02-15T10:30:00Z",
  "payload": {
    "model": {
      "name": "fraud_detection_model",
      "version": "v1.0.0"
    },
    "recommendation": {
      "label": "approve",
      "confidence_score": 0.98
    }
  }
}
```
