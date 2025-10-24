import psycopg2
from colorama import Fore, Style


BOLD = '\033[1m'
RESET = Style.RESET_ALL


def create_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="mzansi_market",
        user="postgres",
        password="mypassword"
    )
    print("Database connection established")
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    create_stall_owners_table = """
    CREATE TABLE IF NOT EXISTS Stall_Owners (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE,
        location VARCHAR(100) NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    """

    create_products_table = """
    CREATE TABLE IF NOT EXISTS Products (
        id SERIAL PRIMARY KEY,
        owner_id INTEGER NOT NULL REFERENCES Stall_Owners(id),
        name VARCHAR(100) NOT NULL UNIQUE,
        price NUMERIC(10,2) NOT NULL,
        stock INTEGER NOT NULL
    );
    """

    create_sales_table = """
    CREATE TABLE IF NOT EXISTS Sales (
        id SERIAL PRIMARY KEY,
        product_id INTEGER NOT NULL REFERENCES Products(id),
        quantity INTEGER NOT NULL,
        total_amount DOUBLE PRECISION NOT NULL,
        sale_date DATE NOT NULL
    );
    """

    cursor.execute(create_stall_owners_table)
    cursor.execute(create_products_table)
    cursor.execute(create_sales_table)

    conn.commit()
    print("Tables created successfully.")

    cursor.close()
    conn.close()
    

def add_stall_owner(cursor, name, location, password):
  
    cursor.execute("""
            INSERT INTO Stall_Owners (name, location, password)
            VALUES (%s, %s, %s)
        """, (name, location, password))

def get_product(cursor,name, price, stock, owner_id):
    cursor.execute( """
                   INSERT INTO Products (name, price, stock, owner_id)
                   VALUES (%s, %s, %s, %s)
                    """, (name, price, stock, owner_id))

def get_sale( cursor,product_id, quantity, total_amount):
      cursor.execute("""
            INSERT INTO Sales (product_id, quantity, total_amount, sale_date)
            VALUES (%s, %s, %s, CURRENT_DATE)
        """, (product_id, quantity, total_amount))
      cursor.execute("UPDATE Products SET stock = stock - %s WHERE id = %s", (quantity, product_id))
      cursor.execute("""
            SELECT p.id, p.name, p.price, p.stock, s.name AS owner_name
            FROM Products p
            JOIN Stall_Owners s ON p.owner_id = s.id
        """)


def get_login(cursor, name, password):
    cursor.execute("""
            SELECT * FROM Stall_Owners 
            WHERE LOWER(name) = LOWER(%s) AND password = %s
        """, (name, password))

def display_product(cursor , owner_id):
     cursor.execute("""
            SELECT name, price, stock FROM Products WHERE owner_id = %s
        """, (owner_id,))
        
    
  


# -- Product Functions --



create_tables()
