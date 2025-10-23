import psycopg2
import csv
from datetime import datetime
from db_setup import create_tables


def get_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mzansi_market",
            user="postgres",
            password="12345"
        )
        return conn
    except Exception as e:
        print("❌ Database connection error:", e)
        return None


# -- Stall Owner --
def add_stall_owner(name, location):
    try:
        conn = get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO stall_owners (name, location) VALUES (%s, %s) RETURNING id;",
            (name, location)
        )
        owner_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Stall owner '{name}' added successfully with ID {owner_id}!")
        return owner_id
    except Exception as e:
        print("❌ Error adding stall owner:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()


def select_stall_owner():
    try:
        conn = get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM stall_owners;")
        owners = cursor.fetchall()
        if not owners:
            print("⚠️ No stall owners found. Add one first.")
            return None
        print("\n🏪 Stall Owners:")
        for owner in owners:
            print(f"{owner[0]}. {owner[1]}")
        owner_id = int(input("Select Stall Owner ID: "))
        return owner_id
    except Exception as e:
        print("❌ Error selecting stall owner:", e)
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


# -- Product --
def add_product(owner_id, name, price, stock):
    try:
        conn = get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (owner_id, name, price, stock) VALUES (%s, %s, %s, %s) RETURNING id;",
            (owner_id, name, price, stock)
        )
        product_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Product '{name}' added successfully with ID {product_id}!")
        return product_id
    except Exception as e:
        print("❌ Error adding product:", e)
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()


def view_products():
    try:
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM products;")
        products = cursor.fetchall()
        if not products:
            print("ℹ️ No products found in the database.")
            return
        print("\n📦 Available Products:")
        print("-" * 40)
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Price: R{product[2]:.2f}, Stock: {product[3]}")
        print("-" * 40)
    except Exception as e:
        print("❌ Error viewing products:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()


# -- Sales --
def make_sale(product_input, quantity):
    try:
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()

        try:
            product_id = int(product_input)
            cursor.execute("SELECT id, name, price, stock FROM products WHERE id = %s;", (product_id,))
        except ValueError:
            cursor.execute("SELECT id, name, price, stock FROM products WHERE name = %s;", (product_input,))

        product = cursor.fetchone()
        if not product:
            print("❌ Product not found.")
            return

        product_id, product_name, price, stock = product
        if stock < quantity:
            print("❌ Insufficient stock.")
            return

        total_amount = price * quantity
        sale_date = datetime.now()

        cursor.execute(
            "INSERT INTO sales (product_id, quantity, total_amount, sale_date) VALUES (%s, %s, %s, %s);",
            (product_id, quantity, total_amount, sale_date)
        )
        cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s;", (quantity, product_id))
        conn.commit()
        print(f"✅ Sale recorded: {quantity} x {product_name} for R{total_amount:.2f}")

    except Exception as e:
        print("❌ Error making sale:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()


# -- Weekly Report --
def weekly_report():
    try:
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, SUM(s.quantity) AS total_sold, SUM(s.total_amount) AS total_revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.name;
        """)
        report = cursor.fetchall()
        if not report:
            print("No sales data available for this week.")
            return
        print("\n📊 Weekly Sales Report:")
        print("-" * 50)
        for row in report:
            print(f"Product: {row[0]}, Total Sold: {row[1]}, Total Revenue: R{row[2]:.2f}")
        print("-" * 50)
    except Exception as e:
        print("❌ Error generating report:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()


# -- Export CSV --
def export_report_to_csv():
    try:
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.name AS product_name,
                so.name AS owner_name,
                so.location AS stall_location,
                p.price AS price_per_item,
                p.stock AS current_stock,
                SUM(s.quantity) AS total_sold,
                SUM(s.total_amount) AS total_revenue
            FROM products p
            JOIN stall_owners so ON p.owner_id = so.id
            LEFT JOIN sales s ON s.product_id = p.id
            GROUP BY p.id, p.name, so.name, so.location, p.price, p.stock
            ORDER BY so.name, p.name;
        """)
        report = cursor.fetchall()

        import pandas as pd
        df_report = pd.DataFrame(report, columns=[
            "Product", "Owner", "Location", "Price per Item", "Current Stock", "Total Sold", "Total Revenue"
        ])

        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"weekly_report_{date_str}.csv"

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(df_report.columns)
            for row in report:
                product = row[0]
                owner = row[1]
                location = row[2]
                price = f"R{float(row[3]):.2f}"
                stock = row[4]
                total_sold = int(row[5]) if row[5] is not None else 0
                total_revenue = f"R{float(row[6]):.2f}" if row[6] is not None else "R0.00"
                writer.writerow([product, owner, location, price, stock, total_sold, total_revenue])

        print(f"✅ Weekly report exported successfully to {filename}!")

    except Exception as e:
        print("❌ Error exporting report to CSV:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()


# -- Search Products --
def search_products():
    try:
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        search_term = input("🔍 Enter product name to search: ").strip()
        cursor.execute("""
            SELECT p.id, p.name, p.price, p.stock, so.name AS owner_name, so.location
            FROM products p
            JOIN stall_owners so ON p.owner_id = so.id
            WHERE p.name ILIKE %s;
        """, (f"%{search_term}%",))
        results = cursor.fetchall()
        if not results:
            print("❌ No products found matching your search.")
            return
        print("\n🔎 Search Results:")
        print("-" * 60)
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Price: R{row[2]:.2f}, Stock: {row[3]}, Owner: {row[4]}, Location: {row[5]}")
        print("-" * 60)
    except Exception as e:
        print("❌ Error searching products:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()


# -- Main Menu --
def main():
    print("🌍 Sawubona! Welcome to Mzansi Market Tracker!")
    create_tables()

    menu = {
        "1": "Add Stall Owner",
        "2": "Add Product",
        "3": "View Products",
        "4": "Make Sale",
        "5": "Weekly Report",
        "6": "Export Weekly Report to CSV",
        "7": "Search Products",
        "8": "Exit"
    }

    current_owner_id = None

    while True:
        print("\n===== Mzansi Market Menu =====")
        for key, value in menu.items():
            print(f"{key}. {value}")
        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter stall owner name: ")
            location = input("Enter stall location: ")
            current_owner_id = add_stall_owner(name, location)

        elif choice == "2":
            if not current_owner_id:
                current_owner_id = select_stall_owner()
                if not current_owner_id:
                    continue
            product_name = input("Enter product name: ")
            price = float(input("Enter product price: "))
            quantity = int(input("Enter product quantity: "))
            add_product(current_owner_id, product_name, price, quantity)

        elif choice == "3":
            view_products()

        elif choice == "4":
            product_name = input("Enter product sold: ")
            quantity = int(input("Enter quantity sold: "))
            make_sale(product_name, quantity)

        elif choice == "5":
            weekly_report()

        elif choice == "6":
            export_report_to_csv()

        elif choice == "7":
            search_products()

        elif choice == "8":
            print("👋 Exiting the program. Hamba kahle!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
