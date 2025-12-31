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
        selection: Selection = self.server.selection
        parsed_url = urlparse(self.path)
        path = parsed_url.path.lstrip("/")

        if path == 'value':
            self._send_text(200, selection.selected_value)

        elif path in selection.selection_names:
            query_params = parse_qs(parsed_url.query)

            if 'select' in query_params:
                # Proper boolean parsing from string
                val = query_params['select'][0].lower()
                is_selected = val in ['true', '1', 'yes']

                if is_selected:
                    selection.select(path)
                self._send_json(200, {"status": "success", "selected": path})
            else:
                is_selected = (selection.selected_value == path)
                self._send_json(200, {'name': path, 'is_selected': is_selected })

        else:
            html = "<h1>Available Selections</h1><ul>"
            for name in selection.selection_names:
                active = " (Active)" if selection.selected_value == name else ""
                html += f"<li><a href='/{name}?select=true'>{name}</a>{active}</li>"
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

    def _send_text(self, status, data: str):
        self.send_response(status)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(data.encode("utf-8"))

class SelectionWebServer:
    def __init__(self, selection: Selection,  host='0.0.0.0', port=8000):
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

