
import random
import uuid
import time
from provit_sdk import ProVitClient

# --- 1. SETUP (Do this once when your app starts) ---
print("Initializing Banking App with ProVit AI Supervision...")

# pointing to your local mock server for now
sdk = ProVitClient(
    api_key="prod-key-778899",
    api_url="http://127.0.0.1:8080", 
    debug=True 
)

# --- 2. YOUR BUSINESS LOGIC ---
def process_loan_application(user_name, amount):
    application_id = str(uuid.uuid4())
    print(f"\nProcessing Loan: {user_name} asking for ${amount}")
    
    # Simulate AI Model Logic
    risk_score = random.uniform(0.1, 0.99)
    decision = "APPROVED" if risk_score > 0.4 else "REJECTED"
    
    # Simulate some processing time
    time.sleep(0.1) 
    
    print(f"  > AI Model Output: {decision} (Confidence: {risk_score:.2f})")

    # --- 3. CAPTURE EVIDENCE (The Integration Point) ---
    # Call the SDK. It's non-blocking, so your app won't slow down.
    sdk.ai_runtime(
        decision_id=application_id,
        model_name="loan-risk-v2",
        model_version="2.1.0",
        label=decision,
        confidence_score=risk_score
    )
    
    print("  > Evidence sent to ProVit ✔️")
    return decision

# --- Run the Mock App ---
if __name__ == "__main__":
    process_loan_application("Alice Smith", 50000)
    process_loan_application("Bob Jones", 12000)
    
    # Keep script alive briefly to let background threads finish sending
    time.sleep(1)
