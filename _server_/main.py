from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import json
import scrape
import random
import string

current_jobs = {}


def random_str(len):
    return ''.join(random.choices(string.ascii_letters, k=len))


class handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

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
            case "/download_start":
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)

                try:
                    data = json.loads(body)
                    sub_ids = data.get("sub_ids")
                except:
                    self.send_response(400)
                    self._set_headers()
                    return

                job_id = random_str(16)
                while job_id in current_jobs:
                    job_id = random_str(16)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._set_headers()
                self.wfile.write(json.dumps({"job_id": job_id}).encode())
                self.wfile.flush()

                current_jobs[job_id] = {
                    'progress': 0,
                    'time': datetime,
                    'result_path': '',
                }

                scrape.start_download(sub_ids, current_jobs[job_id])
            case "/download_progress":
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)

                try:
                    data = json.loads(body)
                    job_id = data.get("job_id")
                except:
                    self.send_response(400)
                    self._set_headers()
                    return

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._set_headers()
                job = current_jobs[job_id]
                self.wfile.write(
                    json.dumps(
                        {'progress': int(job['done'] / job['done_max'] * 100)}
                    ).encode()
                )
                self.wfile.flush()
            case "/download":
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)

                try:
                    data = json.loads(body)
                    job_id = data.get("job_id")
                except:
                    self.send_response(400)
                    self._set_headers()
                    return

                with open(current_jobs[job_id]['result_path'], "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Access-Control-Expose-Headers', 'Content-Disposition')
                self.send_header(
                    'Content-Disposition',
                    'attachment; filename="'
                    + current_jobs[job_id]['result_name']
                    + '"',
                )
                self._set_headers()
                self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8986), handler)
    server.serve_forever()
