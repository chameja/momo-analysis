from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import base64


rides = [
    {"id": 1, "driver": "John Doe", "pickup": "Kigali Heights", "destination": "Kimironko Market", "status": "ongoing"},
    {"id": 2, "driver": "Jane Smith", "pickup": "Remera", "destination": "Downtown Kigali", "status": "completed"}
]

# basic authentication
USERNAME = "admin"
PASSWORD = "secret"

class MotoTaxiHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def _check_auth(self):
        """Check for Basic Auth and validate username/password"""
        auth_header = self.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Basic "):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="MotoTaxiAPI"')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Authentication required"}).encode())
            return False

        # Decode base64 string: "Basic YWRtaW46c2VjcmV0"
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)

        if username == USERNAME and password == PASSWORD:
            return True
        else:
            self.send_response(403)  
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid credentials"}).encode())
            return False

    def do_GET(self):
        if not self._check_auth():
            return

        if self.path == "/rides":
            self._set_headers()
            self.wfile.write(json.dumps({"rides": rides}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    def do_POST(self):
        if not self._check_auth():
            return

        if self.path == "/rides":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                ride_data = json.loads(body)
                new_id = len(rides) + 1
                ride_data["id"] = new_id
                rides.append(ride_data)

                self._set_headers(201)
                self.wfile.write(json.dumps({
                    "message": "Ride created successfully",
                    "ride": ride_data
                }).encode())
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())


def run(server_class=HTTPServer, handler_class=MotoTaxiHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f" Moto Taxi API running at http://localhost:{port}/rides")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
