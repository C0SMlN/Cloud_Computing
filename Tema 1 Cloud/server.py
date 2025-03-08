import json
from database_handler import handler
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


db_handler = handler()

# clasa principala a sv http
class DealershipAPI(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _parse_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            return json.loads(self.rfile.read(content_length).decode('utf-8'))
        return {}

    def do_GET(self):

        parsed_path = urlparse(self.path)
        path_segments = parsed_path.path.strip('/').split('/')

        if path_segments[0] == "cars":
            if len(path_segments) == 1:
                self._set_headers(200)
                self.wfile.write(json.dumps(db_handler.get_cars()).encode())
            elif len(path_segments) == 2:
                car = db_handler.get_car_by_id(path_segments[1])
                if car:
                    self._set_headers(200)
                    self.wfile.write(json.dumps(car).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Car not found"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path_segments = parsed_path.path.strip('/').split('/')

        if path_segments[0] == "cars":
            data = self._parse_body()
            brand = data.get('brand')
            model = data.get('model')
            price = data.get('price')
            year = data.get('year')
            stock = data.get('stock')
            if not brand or not model or not year or not price or not stock:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing fields"}).encode())
                return
            db_handler.add_car(brand, model, price, year, stock)
            self._set_headers(201)
            self.wfile.write(json.dumps({"message": "Car added", "car": data}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_PUT(self):
        parsed_path = urlparse(self.path)
        path_segments = parsed_path.path.strip('/').split('/')

        if path_segments[0] == "cars" and len(path_segments) > 1:
            car_id = int(path_segments[1])
            data = self._parse_body()
            db_handler.update_car(data, car_id)
            self._set_headers(200)
            self.wfile.write(json.dumps({"message": "Car details updated! <3"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        path_segments = parsed_path.path.strip('/').split('/')

        if path_segments[0] == "cars" and len(path_segments) > 1:
            car_id = int(path_segments[1])
            self._set_headers(200)
            db_handler.delete_car(car_id)
            self.wfile.write(json.dumps({"message": "Car deleted"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

# pornire server
def run(server_class=HTTPServer, handler_class=DealershipAPI, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
