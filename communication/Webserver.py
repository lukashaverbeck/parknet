from http.server import HTTPServer, BaseHTTPRequestHandler

from projektkurs.communication.Communication import Communication


class Serv(BaseHTTPRequestHandler):


    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(404)
            self.end_headers()
        else:
            file_to_open = "<h1>GET</h1>"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        responseText = bytes(body).decode("utf-8")
        txtSplit = responseText.split("=" , 1)
        print("Content: " + str(txtSplit))
        Communication.triggerEvent(txtSplit[0] , txtSplit[1])
        self.wfile.write(bytes("<h1> POST</h1>", 'utf-8'))


httpd = HTTPServer(('192.168.178.156', 80), Serv)
httpd.serve_forever()
