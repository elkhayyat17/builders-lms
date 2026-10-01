import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class BuildersHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Route / and /lms and /courses to index.html
        path = self.path.split('?')[0].rstrip('/')
        if path in ['', '/', '/lms', '/courses', '/courses/new']:
            self.path = '/preview.html'
        return super().do_GET()

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), BuildersHandler) as httpd:
        print(f"Builders LMS running at http://localhost:{PORT}/lms")
        httpd.serve_forever()
