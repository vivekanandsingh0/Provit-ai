import http.server
import socketserver
import json
from datetime import datetime

PORT = 8080

class ProVitMockHandler(http.server.BaseHTTPRequestHandler):
    """
    Simulates the ProVit Platform /v1/events endpoint.
    It receives POST requests, validates the JSON, and prints the evidence.
    """
    
    def log_message(self, format, *args):
        # Suppress default log messages to keep terminal clean
        return

    def do_POST(self):
        if self.path == '/v1/events':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Parse JSON payload
                data = json.loads(post_data.decode('utf-8'))
                
                # Verify Authorization Header
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith("Bearer "):
                    self.send_response(401)
                    self.end_headers()
                    print(f"\n[Server] ❌ Unauthorized Request (Missing Bearer Token)")
                    return

                # Print Received Evidence
                print("\n" + "="*50)
                print(f"[Server] ✅ Received AI Evidence at {datetime.now().strftime('%H:%M:%S')}")
                print(f"[Server] Token: {auth_header}")
                print("-" * 50)
                print(json.dumps(data, indent=2))
                print("="*50 + "\n")
                
                # Respond with success
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "received"}).encode('utf-8'))
                
            except json.JSONDecodeError:
                print(f"\n[Server] ❌ Invalid JSON Received")
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    print(f"Starting Mock ProVit Server on port {PORT}...")
    print("Waiting for SDK events...")
    
    # Allow address reuse to prevent "Address already in use" errors on restart
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), ProVitMockHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
