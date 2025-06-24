from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import scrape


class handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == "/download":
            with open("cache/test.zip", "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Disposition', 'attachment; filename="file.zip"')
            self._set_headers()
            self.wfile.write(content)

    def do_POST(self):
        match self.path:
            case "/search":
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)

                try:
                    data = json.loads(body)
                    title = data.get("title")
                except:
                    self.send_response(400)
                    self._set_headers()
                    return

                self.send_response(200)
                self._set_headers()
                response = json.dumps(scrape.search(title))
                self.wfile.write(response.encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8986), handler)
    server.serve_forever()
