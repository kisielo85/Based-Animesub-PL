from http.server import BaseHTTPRequestHandler, HTTPServer

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/download":
            with open("cache/test.zip", "rb") as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Disposition', 'attachment; filename="file.zip"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8986), handler)
    server.serve_forever()