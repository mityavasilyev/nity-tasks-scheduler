import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from dramatiq import middleware


class SimpleHealthCheck(middleware.Middleware):
    """Simple health check middleware that returns 200 OK"""

    def __init__(self, port: int = 8080):
        self.port = port
        threading.Thread(target=self._run_server, daemon=True).start()

    def _run_server(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'OK')
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                # Suppress logging
                pass

        server = HTTPServer(('', self.port), Handler)
        server.serve_forever()