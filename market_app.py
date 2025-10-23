import psycopg2
import csv
from colorama import Fore, Style, init
from db_setup import create_tables

# Initialize colorama
init(autoreset=True)


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
        print(Fore.GREEN + f"🎉 Stall owner '{name}' added successfully with ID {owner_id}.")
        return owner_id
    except Exception as e:
        print(Fore.RED + f"⚠️ Error adding stall owner: {e}")
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
        print(Fore.GREEN + f"🛍️ Product '{name}' added successfully with ID {product_id}.")
        return product_id
    except Exception as e:
        print(Fore.RED + f"⚠️ Error adding product: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def make_sale(product_name, quantity):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, price, stock FROM Products WHERE name = %s;", (product_name,))
        product = cursor.fetchone()

        if not product:
            print(Fore.RED + "❌ Product not found.")
            return
        product_id, price, stock = product

        if stock < quantity:
            print(Fore.YELLOW + "😕 Not enough stock available.")
            return

        total_amount = price * quantity

        cursor.execute("UPDATE Products SET stock = stock - %s WHERE id = %s;", (quantity, product_id))

        cursor.execute("""
            INSERT INTO Sales (product_id, quantity, total_amount, sale_date)
            VALUES (%s, %s, %s, NOW())
            RETURNING id;
        """, (product_id, quantity, total_amount))
        sale_id = cursor.fetchone()[0]

        conn.commit()
        print(Fore.GREEN + f"💸 Sale successful! ID: {sale_id}, Product: '{product_name}', Qty: {quantity}, Total: R{total_amount:.2f}")
        return sale_id

    except Exception as e:
        print(Fore.RED + f"⚠️ Error making sale: {e}")
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

        print(Fore.CYAN + "\n📈 Weekly Sales Report:")
        if not report:
            print(Fore.YELLOW + "No sales recorded in the last 7 days.")
        else:
            for product_name, total_sold, total_revenue in report:
                print(Fore.WHITE + f"🧾 {product_name}: {total_sold} sold | Revenue: R{total_revenue:.2f}")
        return report

    except Exception as e:
        print(Fore.RED + f"⚠️ Error generating weekly report: {e}")
    finally:
        cursor.close()
        conn.close()


def export_report_to_csv(data, filename="weekly_report.csv"):
    if not data:
        print(Fore.YELLOW + "⚠️ No data to export.")
        return

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Product Name", "Total Sold", "Total Revenue"])
        for row in data:
            writer.writerow(row)
    print(Fore.GREEN + f"📤 Report successfully exported to {filename}")


def view_products():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM Products;")
        products = cursor.fetchall()

        print(Fore.CYAN + "\n🛒 Available Products:")
        if not products:
            print(Fore.YELLOW + "No products available.")
        else:
            for pid, name, price, stock in products:
                print(Fore.WHITE + f"🔹 ID: {pid} | {name} | 💰 R{price:.2f} | 📦 Stock: {stock}")
    except Exception as e:
        print(Fore.RED + f"⚠️ Error viewing products: {e}")
    finally:
        cursor.close()
        conn.close()


def main():
    print(Fore.MAGENTA + Style.BRIGHT + "🇿🇦 Welcome to Mzansi Market Tracker! 🇿🇦")
    create_tables()

    menu = {
        "1": "➕ Add Stall Owner",
        "2": "🛒 Add Product",
        "3": "📦 View Products",
        "4": "💵 Make Sale",
        "5": "📊 View Weekly Report",
        "6": "📁 Export Report to CSV",
        "7": "❎ Exit Program"
    }

    while True:
        print(Fore.BLUE + "\n━━━ MENU ━━━")
        for key, value in menu.items():
            print(Fore.WHITE + f"{key}. {value}")

        choice = input(Fore.CYAN + "\nEnter your choice: ").strip()

        try:
            if choice == "1":
                name = input("Enter stall owner name: ")
                location = input("Enter location: ")
                add_stall_owner(name, location)

            elif choice == "2":
                owner_id = input("Enter stall owner ID: ")
                name = input("Enter product name: ")
                price = float(input("Enter product price: "))
                stock = int(input("Enter product stock: "))
                add_product(owner_id, name, price, stock)

            elif choice == "3":
                view_products()

            elif choice == "4":
                product_name = input("Enter product name: ")
                quantity = int(input("Enter quantity sold: "))
                make_sale(product_name, quantity)

            elif choice == "5":
                weekly_report()

            elif choice == "6":
                report = weekly_report()
                export_report_to_csv(report)

            elif choice == "7":
                print(Fore.GREEN + "👋 Thank you for using Mzansi Market Tracker. Sala kahle!")
                break

            else:
                print(Fore.RED + "❌ Invalid option. Try again.")

        except Exception as e:
            print(Fore.RED + f"⚠️ Error: {e}")


if __name__ == "__main__":
    main()
