
import sys
import uuid
from provit_sdk import ProVitClient

# --- Check Dependencies ---
try:
    from transformers import pipeline
except ImportError:
    print("❌ Transformer library missing.")
    print("Please install: pip install transformers torch")
    sys.exit(1)

# --- Initialize ProVit SDK ---
# Note: Using your local mock server
print("Initializing ProVit SDK...")
provit = ProVitClient(
    api_key="huggingface-demo-key",
    api_url="http://127.0.0.1:8080",
    debug=True
)

def run_sentiment_analysis():
    print("\n--- 1. Loading Hugging Face Model (DistilBERT) ---")
    # This automatically downloads the model (~250MB) if not cached locally
    sentiment_task = pipeline("sentiment-analysis")
    
    # Test Cases
    reviews = [
        ("user_101", "I absolutely love this product! It changed my life."),
        ("user_102", "This is the worst service I have ever received."),
        ("user_103", "It's okay, not great but does the job.")
    ]
    
    print("\n--- 2. Running Inference & Capturing Evidence ---")
    
    for user_id, text in reviews:
        # Run AI Inference
        result = sentiment_task(text)[0] # Returns {'label': 'POSITIVE', 'score': 0.99}
        
        label = result['label']
        confidence = result['score']
        
        print(f"\nReview from {user_id}: '{text}'")
        print(f"  > Model Says: {label} (Confidence: {confidence:.4f})")
        
        # Capture Evidence via ProVit SDK
        provit.ai_runtime(
            decision_id=f"review-{user_id}-{uuid.uuid4().hex[:6]}",
            model_name="distilbert-base-uncased-finetuned-sst-2-english",
            model_version="huggingface-hub-latest",
            label=label,
            confidence_score=confidence
        )
        print("  > Evidence sent to ProVit ✔️")

if __name__ == "__main__":
    run_sentiment_analysis()
