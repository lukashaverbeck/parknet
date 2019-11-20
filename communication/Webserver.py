from http.server import HTTPServer, BaseHTTPRequestHandler

import NetworkScan
from Communication import Communication


class Serv(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(404)
            self.end_headers()
        else:
            file_to_open = "<h1>GET</h1>"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, "utf-8"))

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes("<h1>POST</h1>", "utf-8"))
        
        response = bytes(body).decode("utf-8")
        response_data = response.split("=" , 1)
        print("Content: " + str(response_data))
        
        communication = Communication()
        communication.trigger_event(response_data[0] , response_data[1])


httpd = HTTPServer((NetworkScan.get_local_ip(), 80), Serv)
httpd.serve_forever()
