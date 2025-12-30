import json
import threading
import logging
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from selection import Selection
from typing import List, Dict, Any


class SimpleRequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # suppress access logging
        pass

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        if 'select' in query_params:
            name = query_params['name'][0]
            if name in self.server.selection.selection_names:
                self.server.selection.select(name)
                self._send_json(200, {"status": "success", "selected": name})
            else:
                valid_names = ", ".join(self.server.selection.selection_names)
                self._send_json(400, {"error": f"Supported names: {valid_names}"})
        else:
            html = "<h1>Available Selections</h1><ul>"
            for name in self.server.selection.selection_names:
                # Ensure name is handled as a string
                html += f"<li><a href='?name={name}'>{name}</a></li>"
            html += "</ul>"
            self._send_html(200, html)

    def _send_html(self, status, message):
        self.send_response(status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))

    def _send_json(self, status, data: Dict[str, Any]):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

class SelectionWebServer:
    def __init__(self, selection: Selection,  host='0000', port=8000):
        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        self.server = HTTPServer(self.address, SimpleRequestHandler)
        self.server.selection = selection
        self.server_thread = None

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        logging.info(f"web server started http://{self.host}:{self.port}")

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        logging.info("web server stopped")

