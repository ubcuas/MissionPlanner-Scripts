from http.server import HTTPServer, BaseHTTPRequestHandler
import time


class GComHandler(BaseHTTPRequestHandler):
    queue = [[1000, 200, 350],[5000, 230, 450],[500, 120, 250]]
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
        output = ''
        output += "<html><body>"
        output += "<h1>WayPoints</h1>"

        for task in self.queue:
            for terms in task:
                output += str(terms) + " "

            output += "</br>"
        
        output += "</body></html>"
        self.wfile.write(output.encode())

def run():
    PORT = 9000
    server = HTTPServer(('', PORT), GComHandler)
    print("Server running on port %s" % PORT)
    server.serve_forever()

if __name__ == "__main__":
    run()

