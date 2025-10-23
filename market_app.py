import psycopg2
from datetime import date
import csv
from colorama import Fore, Style

# Bold text
BOLD = '\033[1m'
RESET = Style.RESET_ALL

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="mzansi_market",
        user="postgres",
        password="mypassword"
    )

# ---------------- Stall Owner Functions ----------------
def register_stall_owner():
    conn = get_connection()
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

def login_stall_owner():
    conn = get_connection()
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
            return owner  # return the logged-in user info
        else:
            print(Fore.RED + "❌ Invalid login credentials." + RESET)
            return None
    except Exception as e:
        print(Fore.RED + f"❌ Error during login: {e}" + RESET)
        return None
    finally:
        cursor.close()
        conn.close()

# ---------------- Product Functions ----------------
def add_product(owner_id=None):
    conn = get_connection()
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

def view_my_products(owner_id):
    conn = get_connection()
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
    conn = get_connection()
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

# ---------------- Dashboard ----------------
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

# ---------------- Menus ----------------
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

# ---------------- Main Menu ----------------
def main():
    print(Fore.CYAN + BOLD + "🌍 Sawubona! Welcome to Mzansi Market Tracker!" + RESET)

    while True:
        print("\n" + BOLD + "===== 🛍️ Mzansi Market Menu =====" + RESET)
        print(Fore.YELLOW + BOLD + " 1️⃣  Add Stall Owner 📝" + RESET)
        print(Fore.YELLOW + BOLD + " 2️⃣  Login 🔐" + RESET)
        print(Fore.YELLOW + BOLD + " 3️⃣  Add Product 🛒" + RESET)
        print(Fore.YELLOW + BOLD + " 4️⃣  View Products 👀" + RESET)
        print(Fore.YELLOW + BOLD + " 5️⃣  Make Sale 💸" + RESET)
        print(Fore.YELLOW + BOLD + " 6️⃣  Weekly Report 📊" + RESET)
        print(Fore.YELLOW + BOLD + " 7️⃣  Export Weekly Report to CSV 📁" + RESET)
        print(Fore.YELLOW + BOLD + " 8️⃣  Search Product 🔍" + RESET)
        print(Fore.YELLOW + BOLD + " 9️⃣  Exit 🚪" + RESET)

        choice = input(Fore.CYAN + BOLD + "\n👉 Enter your choice: " + RESET).strip()
        if choice == "1":
            register_stall_owner()
        elif choice == "2":
            login_menu()
        elif choice == "3":
            add_product()
        elif choice == "8":
            search_product()
        elif choice == "9":
            print(Fore.GREEN + BOLD + "👋 Goodbye! Thanks for using Mzansi Market Tracker!" + RESET)
            break
        else:
            print(Fore.RED + BOLD + "❌ Invalid menu option. Try again." + RESET)


if __name__ == "__main__":
    main()
