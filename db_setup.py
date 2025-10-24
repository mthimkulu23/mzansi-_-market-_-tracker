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
    

def register_stall_owner():
    conn = create_connection()
    cursor = conn.cursor()
    name = input("👤 Enter your name: ").strip()
    location = input("📍 Enter your location: ").strip()
    password = input("🔑 Create a password: ").strip()

    try:
        cursor.execute("""
            INSERT INTO Stall_Owners (name, location, password)
            VALUES (%s, %s, %s)
        """, (name, location, password))
        conn.commit()
        print(Fore.GREEN + "✅ Registration successful! You can now log in." + RESET)
    except psycopg2.errors.UniqueViolation:
        print(Fore.RED + "❌ Name already exists. Try a different name." + RESET)
        conn.rollback()
    except Exception as e:
        print(Fore.RED + f"❌ Error registering: {e}" + RESET)
    finally:
        cursor.close()
        conn.close()


# -- Product Functions --
def add_product(owner_id=None):
    conn = create_connection()
    cursor = conn.cursor()
    name = input("🛒 Enter product name: ").strip()
    price = float(input("💰 Enter product price: "))
    stock = int(input("📦 Enter product stock: "))
    if owner_id is None:
        owner_id = int(input("🧾 Enter owner ID: "))

    try:
        cursor.execute("""
            INSERT INTO Products (name, price, stock, owner_id)
            VALUES (%s, %s, %s, %s)
        """, (name, price, stock, owner_id))
        conn.commit()
        print(Fore.GREEN + "✅ Product added successfully!" + RESET)
    except Exception as e:
        print(Fore.RED + f"❌ Error adding product: {e}" + RESET)
    finally:
        cursor.close()
        conn.close()


create_tables()
