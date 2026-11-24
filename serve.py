"""Static file server for local development that never lets the browser cache files.
    python serve.py            (serves this folder on http://localhost:8000)
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class NoCache(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()


if __name__ == "__main__":
#     print("Serving on http://localhost:8000")
#     ThreadingHTTPServer(("", 8000), NoCache).serve_forever()

    print("Serving on http://localhost:5173")
    ThreadingHTTPServer(("", 5173), NoCache).serve_forever()