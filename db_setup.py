import psycopg2

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
        location VARCHAR(100) NOT NULL UNIQUE
    );
    """
    
    create_products_table = """
    CREATE TABLE IF NOT EXISTS Products (
        id SERIAL PRIMARY KEY,
        owner_id VARCHAR(50) NOT NULL,
        name VARCHAR(100) NOT NULL UNIQUE,
        price NUMERIC(10,2) NOT NULL,
        stock INTEGER NOT NULL
    );
    """
    
    create_sales_table = """
    CREATE TABLE IF NOT EXISTS Sales (
        id SERIAL PRIMARY KEY,
        product_id VARCHAR(50) NOT NULL,
        quantity INTEGER NOT NULL,
        total_amount DOUBLE PRECISION NOT NULL,
        sale_date DATE NOT NULL
    );
    """

    cursor.execute(create_stall_owners_table)
    cursor.execute(create_products_table)
    cursor.execute(create_sales_table)

   
    print("Tables created successfully.")

create_tables()
