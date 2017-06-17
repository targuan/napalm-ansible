try:
        from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
except:
        from http.server import HTTPServer, BaseHTTPRequestHandler


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(b"{}")
        return

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, Handler)
    while True:
        httpd.handle_request()
