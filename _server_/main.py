from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import scrape

class handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_GET(self):
        if self.path == "/download":
            with open("cache/test.zip", "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Disposition', 'attachment; filename="file.zip"')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(content)

    def do_POST(self):
        print("AUU")
        if self.path == "/search":
            print("AUUGH")
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                data = json.loads(body)
                title = data.get("title")
                print("Odebrany title:", title)
            except:
                pass

            self.send_response(200)
            self._set_cors_headers()
            self.end_headers()
            response=json.dumps(scrape.search(title))
            self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8986), handler)
    server.serve_forever()
