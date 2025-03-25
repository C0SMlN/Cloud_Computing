import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from database_handler import handler

db_handler = handler()
db_handler.creare_tabel()

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

    def _send_error(self, status, message):
        self._set_headers(status)
        self.wfile.write(json.dumps({"error": message}).encode())

    def _add_hateoas_links(self, car):
        # adauga linkuri hateoas la un dict care reprez o masina
        car["_links"] = {
            "self": f"/cars/{car['id']}",
            "update": f"/cars/{car['id']}",
            "delete": f"/cars/{car['id']}"
        }
        return car

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path_segments = parsed_path.path.strip('/').split('/')
        if path_segments[0] == "cars":
            if len(path_segments) == 1:
                cars = db_handler.get_cars()
                cars_with_links = [self._add_hateoas_links(car) for car in cars]
                self._set_headers(200)
                self.wfile.write(json.dumps(cars_with_links).encode())
            elif len(path_segments) == 2:
                try:
                    car_id = int(path_segments[1])
                except ValueError:
                    self._send_error(400, "Invalid car ID")
                    return
                car = db_handler.get_car_by_id(car_id)
                if car:
                    car = self._add_hateoas_links(car)
                    self._set_headers(200)
                    self.wfile.write(json.dumps(car).encode())
                else:
                    self._send_error(404, "Not found")
        else:
            self._send_error(404, "Not found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path_segments = parsed_path.path.strip('/').split('/')
        if len(path_segments) == 1 and path_segments[0] == "cars":
            data = self._parse_body()
            required_fields = ['brand', 'model', 'price', 'year', 'stock']
            if not all(field in data for field in required_fields):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing fields"}).encode())
                return
            car_id = db_handler.add_car(data['brand'], data['model'], data['price'], data['year'], data['stock'])
            new_car = db_handler.get_car_by_id(car_id)
         #   new_car = self._add_hateoas_links(new_car)
            self._set_headers(201)
            self.wfile.write(json.dumps(new_car).encode())
        else:
            self._send_error(404, "Not found")

    def do_PUT(self):
        parsed_path = urlparse(self.path)
        path_segments = parsed_path.path.strip('/').split('/')
        if path_segments[0] == "cars" and len(path_segments) == 2:
            try:
                car_id = int(path_segments[1])
            except ValueError:
                self._send_error(400, "Invalid car ID")
                return
            data = self._parse_body()
            car = db_handler.get_car_by_id(car_id)
            if car:
                db_handler.update_car(data, car_id)
                updated_car = db_handler.get_car_by_id(car_id)
                updated_car = self._add_hateoas_links(updated_car)
                self._set_headers(200)
                self.wfile.write(json.dumps(updated_car).encode())
            else:
                self._send_error(404, "Not found")
        else:
            self._send_error(404, "Not found")

    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        path_segments = parsed_path.path.strip('/').split('/')
        if path_segments[0] == "cars" and len(path_segments) == 2:
            try:
                car_id = int(path_segments[1])
            except ValueError:
                self._send_error(400, "Invalid car ID")
                return
            car = db_handler.get_car_by_id(car_id)
            if car:
                db_handler.delete_car(car_id)
                self._set_headers(200)
                response = {
                    "message": f"Car with ID {car_id} has been deleted.",
                    "_links": {
                        "all_cars": "/cars"
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self._send_error(404, "Not found")
        else:
            self._send_error(404, "Not found")

def run(server_class=HTTPServer, handler_class=DealershipAPI, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
