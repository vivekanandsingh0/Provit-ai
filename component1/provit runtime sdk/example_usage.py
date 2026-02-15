import time
import os
from provit_sdk import ProVitClient

# Usage Example
def main():
    print(" initializing ProVit SDK...")
    
    # In production, use environment variables for sensitive keys
    # API URL is set to a placeholder for demonstration
    client = ProVitClient(
        api_key="demo-api-key-123",
        api_url="http://127.0.0.1:8080",
        debug=True 
    )

    # Mock Decision Context
    decision_id = f"txn-{int(time.time())}"
    model_name = "fraud_detection_model"
    model_version = "v2.3.1"
    
    print(f"\n[App] Processing Transaction: {decision_id}")
    
    # ... AI Inference Happens Here ...
    inference_result = "legitimate"
    confidence = 0.985
    
    print(f"[App] Model Result: {inference_result} ({confidence})")

    # --- SDK INTEGRATION POINT ---
    print("[App] Sending evidence to ProVit (Non-blocking)...")
    
    start_time = time.perf_counter()
    
    client.ai_runtime(
        decision_id=decision_id,
        model_name=model_name,
        model_version=model_version,
        label=inference_result,
        confidence_score=confidence
    )
    
    end_time = time.perf_counter()
    
    # Measure impact
    duration_ms = (end_time - start_time) * 1000
    print(f"[App] SDK Call returned in: {duration_ms:.4f} ms")
    print("[App] Continuing business logic immediately...")

    # Simulating the app staying alive for a bit so the background thread can finish
    # (In a real web server, the process is always running)
    time.sleep(1)
    print("[App] Transaction complete.")

if __name__ == "__main__":
    main()
