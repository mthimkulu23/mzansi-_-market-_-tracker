import psycopg2
from db_setup import create_tables

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="mzansi_market",
        user="postgres",
        password="mypassword"
    )
    return conn

def add_stall_owner(name, location):
    conn = get_connection()
    cursor = conn.cursor()
    insert_query = "INSERT INTO Stall_Owners (name, location) VALUES (%s, %s) RETURNING id;"
    cursor.execute(insert_query, (name, location))
    owner_id = cursor.fetchone()[0]
    
    return owner_id


def add_product(owner_id, name, price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    insert_query = "INSERT INTO Products (owner_id, name, price, stock) VALUES (%s, %s, %s, %s) RETURNING id;"
    cursor.execute(insert_query, (owner_id, name, price, stock))
    product_id = cursor.fetchone()[0]
    
    return product_id




update_stock_query = "UPDATE Products SET stock = stock - %s WHERE name = %s;"

def make_sale(product_name, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    insert_query = "INSERT INTO Sales (product_name, quantity) VALUES (%s, %s) RETURNING id;"
    cursor.execute(insert_query, (product_name, quantity))
    sale_id = cursor.fetchone()[0]
    
    return sale_id


def weekly_report():
    conn = get_connection()
    cursor = conn.cursor()
    report_query = """
    SELECT p.name, SUM(s.quantity) AS total_sold, SUM(s.total_amount) AS total_revenue
    FROM Sales s
    JOIN Products p ON s.product_id = p.id
    WHERE s.sale_date >= NOW() - INTERVAL '7 days'
    GROUP BY p.name;
    """
    cursor.execute(report_query)
    report = cursor.fetchall()
    
    return report




