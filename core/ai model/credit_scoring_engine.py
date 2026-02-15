
import joblib
import pandas as pd
import numpy as np
import os
import uuid
import datetime
from provit_sdk import ProVitClient

MODEL_PATH = "loan_risk_model.pkl"

class CreditScoringEngine:
    """
    Production-grade inference engine for evaluating credit risk.
    Loads trained model and serves predictions.
    Now integrated with ProVit AI Runtime SDK for automated governance.
    """
    
    def __init__(self, model_path=MODEL_PATH, api_url="http://127.0.0.1:8080"):
        self.model_path = model_path
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model artifact '{self.model_path}' missing. Please train model first.")
        
        print(f"[CreditEngine] Loading Model v1.0 from {self.model_path}...")
        self.model = joblib.load(self.model_path)
        self.model_version = "v1.0.0" 
        self.model_name = "random_forest_credit_risk"
        
        # --- SDK Integration ---
        print(f"[CreditEngine] Connecting to ProVit Evidence Node at {api_url}...")
        self.evidence_client = ProVitClient(
            api_key="production-key-123", # In real app, load from os.environ
            api_url=api_url,
            debug=True
        )

    def evaluate_applicant(self, applicant_id: str, income: float, fico: int, dti: float, amount: float):
        """
        Evaluates a single loan application and captures evidence.
        """
        print(f"\n[CreditEngine] Evaluating Applicant {applicant_id}...")
    
        # Construct DataFrame
        input_data = pd.DataFrame([{
            'annual_income': income,
            'fico_score': fico,
            'dti_ratio': dti,
            'loan_amount': amount
        }])
        
        # 1. Inference
        prob_default = self.model.predict_proba(input_data)[0][1]
        prediction = self.model.predict(input_data)[0]
        
        # 2. Business Logic Wrapper
        decision = "REJECTED" if prediction == 1 else "APPROVED"
        risk_level = "High" if prob_default > 0.5 else "Low"
        
        # 3. Capture Evidence (The ProVit "Hand-Off")
        self.evidence_client.ai_runtime(
            decision_id=applicant_id,
            model_name=self.model_name,
            model_version=self.model_version,
            label=decision,
            confidence_score=prob_default
        )
        
        # 4. Log Output
        print(f"  > Decision: {decision} ({risk_level} Risk)")
        print(f"  > Default Probability: {prob_default:.4f}")
        print(f"  > 🔒 Evidence secured via ProVit SDK")
        
        return {
            "applicant_id": applicant_id,
            "decision": decision,
            "confidence_score": float(prob_default),
            "timestamp": datetime.datetime.now().isoformat()
        }

if __name__ == "__main__":
    # --- Integration Test / Simulation ---
    engine = CreditScoringEngine()
    
    # Simulate incoming loan requests
    scenarios = [
        ("app-001-Alice", 120000, 780, 0.15, 20000), # Perfect
        ("app-002-Bob",    35000, 610, 0.55, 15000), # High Risk
        ("app-003-Charlie",65000, 670, 0.42, 30000)  # Borderline
    ]

    for app_id, inc, fico, dti, amt in scenarios:
        result = engine.evaluate_applicant(app_id, inc, fico, dti, amt)
