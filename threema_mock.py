"""
Mock server for the main API endpoint of threema. 
Responds to all GET requests with the list of credentials read from the dummy file.

Just execute it with 

python threema_mock.py

and replace the DEFAULT_BASE_URL in the threemaapi module with "http://<your_ip_address>:8888"
"""

import http.server
import random
import socketserver
import json


class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        students = []
        with open("threema_dummy_data.csv") as data:
            for line in data:
                sid = random.randint(10 ** 5, 10 ** 10)
                username = line.split(",")[0]
                students.append({"id": sid, "username": username})
        self.wfile.write(json.dumps({"credentials": students}).encode("utf-8"))


PORT = 8888

with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
