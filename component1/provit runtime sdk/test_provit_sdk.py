import unittest
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from provit_sdk import ProVitClient

# --- Helpers for Testing ---
RECEIVED_EVENTS = []

class MockTestHandler(BaseHTTPRequestHandler):
    """Minimal handler for capturing requests during unit tests"""
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)
        data = json.loads(body)
        
        # Capture header for auth check
        auth_header = self.headers.get('Authorization')
        
        RECEIVED_EVENTS.append({
            "data": data,
            "auth": auth_header
        })
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
        
    def log_message(self, format, *args):
        pass # Silence logs

def start_test_server(port):
    server = HTTPServer(('127.0.0.1', port), MockTestHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server

# --- Unit Tests ---
class TestProVitSDK(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Start a local test server once for all tests
        cls.test_port = 8888
        cls.server = start_test_server(cls.test_port)
        # Give server a moment to start
        time.sleep(0.1)

    def setUp(self):
        # Clear received events before each test
        global RECEIVED_EVENTS
        RECEIVED_EVENTS = []
        
        self.client = ProVitClient(
            api_key="test-api-key", 
            api_url=f"http://127.0.0.1:{self.test_port}",
            debug=True
        )

    def test_end_to_end_transmission(self):
        """Test that event is correctly formatted and sent."""
        decision_id = "test-decision-001"
        
        self.client.ai_runtime(
            decision_id=decision_id,
            model_name="fraud-v1",
            model_version="1.0.0",
            label="reject",
            confidence_score=0.95
        )
        
        # Wait briefly for async thread to complete
        time.sleep(0.5)
        
        self.assertEqual(len(RECEIVED_EVENTS), 1)
        event = RECEIVED_EVENTS[0]
        
        # Check Auth
        self.assertEqual(event['auth'], "Bearer test-api-key")
        
        # Check Payload Structure
        payload = event['data']
        self.assertEqual(payload['event_type'], "ai.runtime")
        self.assertEqual(payload['decision_id'], decision_id)
        self.assertEqual(payload['payload']['model']['name'], "fraud-v1")
        self.assertEqual(payload['payload']['recommendation']['label'], "reject")
        self.assertEqual(payload['payload']['recommendation']['confidence_score'], 0.95)

    def test_fail_safe_invalid_url(self):
        """Test that SDK does not crash when URL is unreachable."""
        bad_client = ProVitClient(
            api_key="key", 
            api_url="http://127.0.0.1:9999", # Port not listening
            debug=False # Suppress error prints for clean test output
        )
        
        try:
            bad_client.ai_runtime(
                decision_id="fail-test",
                model_name="m", model_version="v", label="l", confidence_score=0.1
            )
        except Exception as e:
            self.fail(f"SDK raised exception {e} instead of failing silently")

    def test_invalid_types_handling(self):
        """Test SDK handles type conversion (e.g. float casting)."""
        self.client.ai_runtime(
            decision_id="type-test",
            model_name="m", model_version="v", 
            label=100, # Int instead of string
            confidence_score="0.88" # String instead of float
        )
        
        time.sleep(0.5)
        
        event = RECEIVED_EVENTS[0]['data']
        rec = event['payload']['recommendation']
        
        # Assert conversions worked
        self.assertIsInstance(rec['label'], str) 
        self.assertEqual(rec['label'], "100")
        
        self.assertIsInstance(rec['confidence_score'], float)
        self.assertEqual(rec['confidence_score'], 0.88)

if __name__ == '__main__':
    unittest.main()
