# ProVit AI Runtime SDK

A lightweight, fire-and-forget Python SDK for capturing AI runtime evidence. Designed for high-assurance environments where model decisions must be auditable without standard logging overhead or latency impact.

## Features
- **Zero Latency Impact:** Dispatches events asynchronously on a background thread (<1ms blocking time).
- **Fail-Safe:** Never crashes the host application; network errors are silently suppressed by default.
- **Traceability:** Automatically generates unique `event_id` and captures metadata (SDK version, Python version).
- **Normalization:** Automatically standardizes labels (e.g., "Approve" -> "approve") for consistent analytics.

## Installation

### Method 1: Local Development (Editable)
Use this if you are developing the SDK or if the source code is on your machine.
```bash
cd "component1/provit runtime sdk"
pip install -e .
```

### Method 2: Production / Other Machines
Copy the SDK folder to your target machine and install it:
```bash
pip install .
```
*(Or install directly from git if hosted: `pip install git+https://github.com/your-org/provit-ai-sdk.git`)*

## Integration Guide

### 1. Initialize the Client
Create the client once when your application starts (e.g., in your `main.py` or service initialization).

```python
from provit_sdk import ProVitClient

# Initialize with your API Key and Endpoint
provit_client = ProVitClient(
    api_key="your-production-key",
    api_url="https://api.provit.ai",  # Or your internal receiver
    debug=True,                       # Set False in production
    normalize_labels=True             # Auto-lowercase labels? (Default: True)
)
```

### 2. Instrumentalize Your Model
Call `ai_runtime()` immediately after your model makes a prediction.

```python
def predict(user_data):
    # ... your AI model logic ...
    decision = model.predict(user_data)
    confidence = model.predict_proba(user_data)
    
    # --- Capture Evidence ---
    provit_client.ai_runtime(
        decision_id="txn-12345",        # Unique ID from your business logic
        model_name="credit-scoring-v1", # Model Identity
        model_version="1.0.0",          
        label=decision,                 # Result (e.g., "Approved")
        confidence_score=confidence     # Probability (0.0 - 1.0)
    )
    
    return decision
```

## Testing & Verification

This SDK includes a **Mock Server** to verify integration locally without needing the real ProVit cloud.

### Step 1: Start the Mock Server
Open a terminal and run:
```bash
python mock_provit_server.py
```
*It will listen on `http://localhost:8080`.*

### Step 2: Run a Test Script
In another terminal, run your application or the included example:
```bash
python example_usage.py
```

You should see the JSON evidence appear in the server terminal, confirming the pipeline works.

## Configuration Options
| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_key` | Required | Your authentication token. |
| `api_url` | `https://api.provit.ai` | The endpoint specific to your environment. |
| `debug` | `False` | If `True`, prints connection errors to stderr. |
| `normalize_labels` | `True` | If `True`, converts labels to lowercase stripped strings. |
