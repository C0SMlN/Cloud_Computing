import sqlite3

class handler:
    def __init__(self, db_name='data.sb'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self. conn.cursor()

    def creare_tabel(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            price INTEGER NOT NULL,
            year INTEGER NOT NULL,
            stock INTEGER
            )""")
        self.conn.commit()

    # localhost:8080/cars/ -> POST creeaza o masina noua
    # localhost:8080/cars/ -> GET toate masinile (
    # localhost:8080/cars/id -> GET detalii despre o masina
    # localhost:8080/cars/id -> PUT actualizeaza
    # localhost:8080/cars/id -> DELETE sterge

    def get_cars(self):
        self.cursor.execute("SELECT * FROM cars")
        rows = self.cursor.fetchall()
        cars = []
        for row in rows:
            car = {
                "id": row[0],
                "brand": row[1],
                "model": row[2],
                "price": row[3],
                "year": row[4],
                "stock": row[5]
            }
            cars.append(car)
        return cars

    def get_car_by_id(self, car_id):
        self.cursor.execute("SELECT * FROM cars WHERE id= ?", car_id)
        row = self.cursor.fetchone()
        if row:
            return{
                    "id": row[0],
                    "brand": row[1],
                    "model": row[2],
                    "price": row[3],
                    "year": row[4],
                    "stock": row[5]
                }
        return None




    def add_car(self, brand, model, price, year, stock):
        self.cursor.execute("INSERT INTO cars (brand, model, price, year, stock) VALUES (?,?,?,?,?)", (brand, model, price, year, stock))
        self.conn.commit()



