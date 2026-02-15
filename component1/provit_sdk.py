import json
import threading
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional

class ProVitClient:
    """
    ProVit AI Runtime SDK (v0)
    
    A lightweight, thread-safe, fire-and-forget SDK for capturing AI evidence.
    """
    
    def __init__(self, api_key: str, api_url: str = "https://api.provit.ai", debug: bool = False):
        """
        Initialize the ProVit SDK Client.
        
        Args:
            api_key (str): The API key for authentication.
            api_url (str): The base URL of the ProVit platform.
            debug (bool): If True, prints errors to stderr. Default False.
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.endpoint = f"{self.api_url}/v1/events"
        self.debug = debug

    def ai_runtime(
        self, 
        decision_id: str, 
        model_name: str, 
        model_version: str, 
        label: str, 
        confidence_score: float
    ):
        """
        Captures AI runtime recommendation evidence.
        
        This method is strictly non-blocking. It spawns a background thread to 
        send the data and returns immediately. All errors during transmission 
        are suppressed to ensure the host AI application is never disrupted.
        
        Args:
            decision_id (str): Unique business decision ID.
            model_name (str): Name of the model used.
            model_version (str): Version of the model.
            label (str): The output/recommendation (e.g., 'approve', 'fraud').
            confidence_score (float): The model's confidence (0.0 - 1.0).
        """
        try:
            # Construct the canonical event structure
            payload = {
                "event_type": "ai.runtime",
                "decision_id": decision_id,
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "payload": {
                    "model": {
                        "name": model_name,
                        "version": model_version
                    },
                    "recommendation": {
                        "label": str(label),
                        "confidence_score": float(confidence_score)
                    }
                }
            }

            # Fire-and-forget: run network request in a daemon thread
            thread = threading.Thread(target=self._send_event, args=(payload,))
            thread.daemon = True  # Ensure thread doesn't block program exit
            thread.start()
            
        except Exception as e:
            if self.debug:
                print(f"[SDK Start Error] {e}")

    def _send_event(self, event_data: dict):
        """
        Internal method to send the event via HTTP POST.
        Suppresses all exceptions.
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "ProVit-SDK-Python/v0.1"
            }
            
            data = json.dumps(event_data).encode('utf-8')
            req = urllib.request.Request(
                self.endpoint, 
                data=data, 
                headers=headers, 
                method='POST'
            )

            # Strict 2-second timeout as per specification
            with urllib.request.urlopen(req, timeout=2) as response:
                # Read response to ensure connection closes cleanly, 
                # but ignore content
                response.read()

        except Exception as e:
            # 10.2 Fail-Safe Behavior:
            # "The SDK must never raise runtime exceptions to the host system."
            # "If ProVit is unreachable, the AI continues normally."
            if self.debug:
                print(f"[SDK Transmission Error] {e}")
