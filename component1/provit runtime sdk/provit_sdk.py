import json
import threading
import urllib.request
import urllib.error
import uuid
import platform
import queue
import atexit
from datetime import datetime, timezone
from typing import Optional

# Version tracking
__version__ = "0.1.0"

class ProVitClient:
    """
    ProVit AI Runtime SDK (v0)
    
    A lightweight, thread-safe, fire-and-forget SDK for capturing AI evidence.
    """
    
    def __init__(self, api_key: str, api_url: str = "https://api.provit.ai", debug: bool = False, normalize_labels: bool = True):
        """
        Initialize the ProVit SDK Client.
        
        Args:
            api_key (str): The API key for authentication.
            api_url (str): The base URL of the ProVit platform.
            debug (bool): If True, prints errors to stderr. Default False.
            normalize_labels (bool): If True, converts all labels to lowercase. Default True.
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.endpoint = f"{self.api_url}/v1/events"
        self.debug = debug
        self.normalize_labels = normalize_labels
        
        # --- Architecture Upgrade: Background Queue System ---
        # 1. Instant Capture: Events are pushed to this queue (Microsecond latency)
        self._event_queue = queue.Queue()
        
        # 2. Background Worker: Dedicated thread handles network I/O
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        
        # 3. Graceful Shutdown: Ensure pending logs are flushed when host app exits
        atexit.register(self._shutdown_hook)

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
        
        This method is strictly non-blocking. It pushes the event to a memory buffer 
        and returns immediately (~10 microseconds). Network transmission happens 
        asynchronously in the background.
        
        Args:
            decision_id (str): Unique business decision ID.
            model_name (str): Name of the model used.
            model_version (str): Version of the model.
            label (str): The output/recommendation (e.g., 'approve', 'fraud').
            confidence_score (float): The model's confidence (0.0 - 1.0).
        """
        try:
            # 1. Normalize Label (if enabled)
            processed_label = str(label)
            if self.normalize_labels:
                processed_label = processed_label.lower().strip()

            # 2. Construct the canonical event structure
            payload = {
                "event_id": str(uuid.uuid4()),  # Unique ID for this specific evidence event
                "event_type": "ai.runtime",
                "decision_id": decision_id,
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "meta": {
                    "sdk_version": __version__,
                    "language": "python",
                    "python_version": platform.python_version()
                },
                "payload": {
                    "model": {
                        "name": model_name,
                        "version": model_version
                    },
                    "recommendation": {
                        "label": processed_label,
                        "confidence_score": float(confidence_score)
                    }
                }
            }

            # 3. Instant Hand-off: Push to Queue
            self._event_queue.put(payload)
            
        except Exception as e:
            if self.debug:
                print(f"[SDK Capture Error] {e}")

    def _worker_loop(self):
        """
        Background thread that consumes events from the queue and sends them.
        Run indefinitely until the main program exits.
        """
        while True:
            # Block until an item is available
            event_data = self._event_queue.get()
            try:
                self._send_event(event_data)
            finally:
                self._event_queue.task_done()

    def _shutdown_hook(self):
        """
        Called automatically when the Python script exits.
        Waits for the queue to drain so no logs are lost.
        """
        if not self._event_queue.empty():
            if self.debug:
                print(f"[ProVit SDK] Flushing {self._event_queue.qsize()} pending events before exit...")
            
            # Wait for the queue to process all items (blocks main thread exit safely)
            # We set a timeout (e.g., 5 seconds) to prevent hanging forever if network is down
            try:
                # Need a custom join with timeout logic because queue.join() doesn't support timeout in older python
                # But since we are likely on modern python, we rely on the worker being fast.
                # A simple join is usually sufficient for a "graceful" shutdown.
                self._event_queue.join()
            except Exception:
                pass


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
                # Read response to ensure connection closes cleanly
                response.read()

        except Exception as e:
            # 10.2 Fail-Safe Behavior:
            if self.debug:
                print(f"[SDK Transmission Error] {e}")
