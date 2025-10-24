import psycopg2
from datetime import date
import csv
from colorama import Fore, Style
from db_setup import create_connection
from db_setup import register_stall_owner
from db_setup import add_product

# Bold text
BOLD = '\033[1m'
RESET = Style.RESET_ALL


# -- Stall Owner Functions --


def login_stall_owner():
    conn = create_connection()
    cursor = conn.cursor()
    name = input("👤 Enter your name: ").strip()
    password = input("🔑 Enter your password: ").strip()

    try:
        cursor.execute("""
            SELECT * FROM Stall_Owners 
            WHERE LOWER(name) = LOWER(%s) AND password = %s
        """, (name, password))
        owner = cursor.fetchone()

        if owner:
            print(Fore.GREEN + f"🎉 Welcome back, {owner[1]}!" + RESET)
            return owner
        else:
            print(Fore.RED + "❌ Invalid login credentials." + RESET)
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error during login: {e}" + RESET)
        return None
    finally:
        cursor.close()
        conn.close()



def view_my_products(owner_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT name, price, stock FROM Products WHERE owner_id = %s
        """, (owner_id,))
        products = cursor.fetchall()
        if products:
            print(Fore.CYAN + BOLD + "\n📋 Your Products:" + RESET)
            for p in products:
                print(f"🛒 {p[0]} | 💰 {p[1]} | 📦 {p[2]}")
        else:
            print(Fore.YELLOW + "ℹ️ No products found." + RESET)
    except Exception as e:
        print(Fore.RED + f"❌ Error fetching products: {e}" + RESET)
    finally:
        cursor.close()
        conn.close()

def search_product():
    conn = create_connection()
    cursor = conn.cursor()
    keyword = input("🔍 Enter product name to search: ").strip()

    try:
        cursor.execute("""
            SELECT p.name, p.price, p.stock, s.name AS owner_name
            FROM Products p
            JOIN Stall_Owners s ON p.owner_id = s.id
            WHERE LOWER(p.name) LIKE LOWER(%s)
        """, (f"%{keyword}%",))
        results = cursor.fetchall()
        if results:
            print(Fore.CYAN + BOLD + "\n📋 Search Results:" + RESET)
            for r in results:
                print(f"🛒 {r[0]} | 💰 {r[1]} | 📦 {r[2]} | 🧑 Owner: {r[3]}")
        else:
            print(Fore.YELLOW + "ℹ️ No products found." + RESET)
    except Exception as e:
        print(Fore.RED + f"❌ Error searching products: {e}" + RESET)
    finally:
        cursor.close()
        conn.close()

# -- Weekly Report Functions --
def generate_weekly_report():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.name, s.name AS owner_name, SUM(sa.quantity) AS total_sold,
                   SUM(sa.quantity * p.price) AS total_revenue
            FROM Sales sa
            JOIN Products p ON sa.product_id = p.id
            JOIN Stall_Owners s ON p.owner_id = s.id
            WHERE sa.sale_date >= current_date - interval '7 days'
            GROUP BY p.name, s.name
            ORDER BY total_sold DESC
        """)
        report = cursor.fetchall()
        if report:
            print(Fore.CYAN + BOLD + "\n📊 Weekly Sales Report:" + RESET)
            print(Fore.YELLOW + "Product | Owner | Total Sold | Total Revenue" + RESET)
            for r in report:
                print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")
        else:
            print(Fore.YELLOW + "ℹ️ No sales in the past week." + RESET)
        return report
    except Exception as e:
        print(Fore.RED + f"❌ Error generating weekly report: {e}" + RESET)
        return []
    finally:
        cursor.close()
        conn.close()
        
        
# -- Make Sale --
def make_sale():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Show all products
        cursor.execute("""
            SELECT p.id, p.name, p.price, p.stock, s.name AS owner_name
            FROM Products p
            JOIN Stall_Owners s ON p.owner_id = s.id
        """)
        products = cursor.fetchall()
        if not products:
            print(Fore.YELLOW + "ℹ️ No products available for sale." + RESET)
            return

        print(Fore.CYAN + BOLD + "\n📋 Available Products:" + RESET)
        for p in products:
            print(f"ID: {p[0]} | 🛒 {p[1]} | 💰 {p[2]} | 📦 Stock: {p[3]} | 🧑 Owner: {p[4]}")

        product_id = int(input("🆔 Enter Product ID to sell: "))
        quantity = int(input("📦 Enter quantity to sell: "))

        # Check stock and get price
        cursor.execute("SELECT stock, price FROM Products WHERE id=%s", (product_id,))
        product = cursor.fetchone()
        if not product:
            print(Fore.RED + "❌ Product not found." + RESET)
            return
        stock, price = product
        if stock < quantity:
            print(Fore.RED + "❌ Not enough stock available." + RESET)
            return

        total_amount = quantity * price

        # Deduct stock
        cursor.execute("UPDATE Products SET stock = stock - %s WHERE id = %s", (quantity, product_id))
        # Insert into Sales table including total_amount
        cursor.execute("""
            INSERT INTO Sales (product_id, quantity, total_amount, sale_date)
            VALUES (%s, %s, %s, CURRENT_DATE)
        """, (product_id, quantity, total_amount))
        conn.commit()
        print(Fore.GREEN + f"✅ Sale recorded successfully! {quantity} unit(s) sold for R{total_amount}." + RESET)

    except Exception as e:
        print(Fore.RED + f"❌ Error making sale: {e}" + RESET)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()




def export_weekly_report_csv():
    report = generate_weekly_report()
    if not report:
        print(Fore.YELLOW + "ℹ️ No data to export." + RESET)
        return

    filename = f"weekly_report_{date.today()}.csv"
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Product", "Owner", "Total Sold", "Total Revenue"])
            for r in report:
                writer.writerow(r)
        print(Fore.GREEN + f"✅ Weekly report exported to {filename}" + RESET)
    except Exception as e:
        print(Fore.RED + f"❌ Error exporting CSV: {e}" + RESET)

# -- Dashboard ----
def user_dashboard(user):
    while True:
        print("\n" + BOLD + f"===== 🏠 Welcome {user[1]} Dashboard =====" + RESET)
        print(Fore.YELLOW + BOLD + " 1️⃣  Add Product 🛒" + RESET)
        print(Fore.YELLOW + BOLD + " 2️⃣  View My Products 👀" + RESET)
        print(Fore.YELLOW + BOLD + " 3️⃣  Logout 🔐" + RESET)

        choice = input(Fore.CYAN + BOLD + "\n👉 Enter your choice: " + RESET).strip()
        if choice == "1":
            add_product(owner_id=user[0])
        elif choice == "2":
            view_my_products(user[0])
        elif choice == "3":
            print(Fore.GREEN + "👋 Logging out..." + RESET)
            break
        else:
            print(Fore.RED + "❌ Invalid option. Try again." + RESET)

# -- Menus ---
def login_menu():
    while True:
        print("\n" + BOLD + "===== 🔐 Login Menu =====" + RESET)
        print(Fore.MAGENTA + BOLD + " 1️⃣ Register" + RESET)
        print(Fore.MAGENTA + BOLD + " 2️⃣ Login" + RESET)
        print(Fore.MAGENTA + BOLD + " 3️⃣ Back to Main Menu" + RESET)

        choice = input(Fore.CYAN + BOLD + "\n👉 Enter your choice: " + RESET).strip()
        if choice == "1":
            register_stall_owner()
        elif choice == "2":
            user = login_stall_owner()
            if user:
                user_dashboard(user)
        elif choice == "3":
            break
        else:
            print(Fore.RED + BOLD + "❌ Invalid option. Try again." + RESET)

# -- Main Menu --
def main():
    print(Fore.CYAN + BOLD + "\n🌍 SAWUBONA! WELCOME TO MZANSI MARKET TRACKER!" + RESET)

    while True:
        print("\n" + BOLD + "="*60 + RESET)
        print(Fore.YELLOW + BOLD + "            🛍️  MZANSI MARKET MENU  🛍️" + RESET)
        print(BOLD + "="*60 + RESET)

        print(Fore.YELLOW + BOLD + "  1️⃣  ADD STALL OWNER 📝" + RESET)
        print(Fore.YELLOW + BOLD + "  2️⃣  LOGIN 🔐" + RESET)
        print(Fore.YELLOW + BOLD + "  3️⃣  ADD PRODUCT 🛒" + RESET)
        print(Fore.YELLOW + BOLD + "  4️⃣  VIEW PRODUCTS 👀" + RESET)
        print(Fore.YELLOW + BOLD + "  5️⃣  MAKE SALE 💸" + RESET)
        print(Fore.YELLOW + BOLD + "  6️⃣  WEEKLY REPORT 📊" + RESET)
        print(Fore.YELLOW + BOLD + "  7️⃣  EXPORT WEEKLY REPORT TO CSV 📁" + RESET)
        print(Fore.YELLOW + BOLD + "  8️⃣  SEARCH PRODUCT 🔍" + RESET)
        print(Fore.YELLOW + BOLD + "  9️⃣  EXIT 🚪" + RESET)
        print(BOLD + "="*60 + RESET)

        choice = input(Fore.CYAN + BOLD + "\n👉 ENTER YOUR CHOICE: " + RESET).strip()
        if choice == "1":
            register_stall_owner()
        elif choice == "2":
            login_menu()
        elif choice == "3":
            add_product()
        elif choice == "5":
            make_sale()
        elif choice == "6":
            generate_weekly_report()
        elif choice == "7":
            export_weekly_report_csv()
        elif choice == "8":
            search_product()
        elif choice == "9":
            print(Fore.GREEN + BOLD + "👋 GOODBYE! THANKS FOR USING MZANSI MARKET TRACKER!" + RESET)
            break
        else:
            print(Fore.RED + BOLD + "❌ INVALID MENU OPTION. TRY AGAIN." + RESET)
            

if __name__ == "__main__":
    main()
