import psycopg2
from db_setup import create_tables

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="mzansi_market",
        user="postgres",
        password="mypassword"
    )


def add_stall_owner(name, location):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO Stall_Owners (name, location)
            VALUES (%s, %s)
            RETURNING id;
        """
        cursor.execute(insert_query, (name, location))
        owner_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Stall owner '{name}' added successfully with ID {owner_id}.")
        return owner_id
    except Exception as e:
        print(f"Error adding stall owner: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_product(owner_id, name, price, stock):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO Products (owner_id, name, price, stock)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        cursor.execute(insert_query, (owner_id, name, price, stock))
        product_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Product '{name}' added successfully with ID {product_id}.")
        return product_id
    except Exception as e:
        print(f"Error adding product: {e}")
        conn.rollback()


def make_sale(product_name, quantity):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get product price and ID
        cursor.execute("SELECT id, price, stock FROM Products WHERE name = %s;", (product_name,))
        product = cursor.fetchone()

        if not product:
            print("Product not found.")
            return
        product_id, price, stock = product

        if stock < quantity:
            print("Not enough stock available.")
            return

        total_amount = price * quantity

 
        update_stock_query = "UPDATE Products SET stock = stock - %s WHERE id = %s;"
        cursor.execute(update_stock_query, (quantity, product_id))


        insert_sale_query = """
            INSERT INTO Sales (product_id, quantity, total_amount, sale_date)
            VALUES (%s, %s, %s, NOW())
            RETURNING id;
        """
        cursor.execute(insert_sale_query, (product_id, quantity, total_amount))
        sale_id = cursor.fetchone()[0]

        conn.commit()
        print(f"Sale made successfully! Sale ID: {sale_id}")
        return sale_id

    except Exception as e:
        print(f"❌ Error making sale: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def weekly_report():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        report_query = """
            SELECT 
                p.name AS product_name,
                SUM(s.quantity) AS total_sold,
                SUM(s.total_amount) AS total_revenue
            FROM Sales s
            JOIN Products p ON s.product_id = p.id
            WHERE s.sale_date >= NOW() - INTERVAL '7 days'
            GROUP BY p.name;
        """
        cursor.execute(report_query)
        report = cursor.fetchall()
        print("Weekly report generated successfully!")
        return report
    except Exception as e:
        print(f" Error generating weekly report: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def main():
    print("🌍 Sawubona! Welcome to Mzansi Market Tracker!")
    create_tables()
    
    

    locations = ("Soweto", "Khayelitsha", "Tembisa", "Umlazi")
    menu = {
        "1": "Add Stall Owner",
        "2": "Add Product",
        "3": "View Products",
        "4": "Make Sale",
        "5": "Weekly Report",
        "6": "Exit"
    }

    while True:
        print("\n Menu:")
        for key, value in menu.items():
            print(f"{key}. {value}")

        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                name = input("Enter stall owner name: ")
                location = input(f"Enter location ({', '.join(locations)}): ")
                add_stall_owner(name, location)

            elif choice == "2":
                owner_id = input("Enter stall owner ID: ")
                name = input("Enter product name: ")
                price = float(input("Enter product price: "))
                stock = int(input("Enter product stock: "))
                add_product(owner_id, name, price, stock)

            elif choice == "3":
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Products;")
                products = cursor.fetchall()
                print("\n📦 Products:")
                for product in products:
                    print(product)
                cursor.close()
                conn.close()

            elif choice == "4":
                product_name = input("Enter product name: ")
                quantity = int(input("Enter quantity sold: "))
                make_sale(product_name, quantity)

            elif choice == "5":
                report = weekly_report()
                print("\n Weekly Sales Report:")
                if not report:
                    print("No sales in the last 7 days.")
                else:
                    for row in report:
                        print(row)

            elif choice == "6":
                print(" Exiting Mzansi Market Tracker. Hamba kahle!")
                break

            else:
                print(" Invalid option. Please try again.")

        except Exception as e:
            print(f" Error: {e}")

if __name__ == "__main__":
    main()
