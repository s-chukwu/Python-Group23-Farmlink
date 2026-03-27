#!/usr/bin/env python3

import sys
import sqlite3
import email
import getpass
import re

def init_db():
    conn = sqlite3.connect("farmlink.db")
    cursor = conn.cursor()

    conn.execute("PRAGMA foreign_keys = ON")

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Farmer', 'Buyer'))
    )
    """)

    # INVENTORY TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER,
        crop_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL,
        status TEXT DEFAULT 'Stored',
        FOREIGN KEY (farmer_id) REFERENCES users(id)
    )
    """)

    # TRANSACTIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER,
        crop_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        FOREIGN KEY (buyer_id) REFERENCES users(id),
        FOREIGN KEY (crop_id) REFERENCES inventory(id)
    )
    """)

    conn.commit()
    conn.close()

# Authentication

# signup
def signup():
    conn = sqlite3.connect("farmlink.db")
    cursor = conn.cursor()
    
    try:
        name = input("Enter your name: ")

        #check if there is an existing user with the inserted email
        while True:
            email = input("Enter your email: ")
            if not is_valid_email(email):
                print("Invalid email format. Please try again.")
                continue
            if not userExists(conn, email):
                break
            print('Account already exists, please enter another one or login')

        # Obscure password while entering it
        password = getpass.getpass("Enter your password: ")

# get valid role
        role = get_valid_role()
        cursor.execute('INSERT INTO users (name, email, password, role) values (?, ?, ?, ?)', (name, email, password, role))
        
        conn.commit() # This saves it to the database
        
        
        print(f"\n Success! '{name}' has been successfully registered as a {role}.")
        
    except sqlite3.IntegrityError:
        print('Database error occurred, please try again')
    except Exception as e:
        print('Unknown error, please try again')
    finally:
         conn.close()

def userExists(conn, email):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    if user is None:
        return False
    else:
        return True

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_valid_role():
    while True:
        try:
            role_choice = int(input("Enter a number that matches who you are registering as: \n 1. Farmer \n 2. Buyer \nYour choice (1 or 2): "))
            if role_choice == 1:
               return "Farmer"
            elif role_choice == 2:
               return "Buyer"
            else:
             print("Please enter a valid choice")
        except ValueError:
            print("Enter a number please! :)")

# Login
def login():
    conn = sqlite3.connect("farmlink.db")
    cursor = conn.cursor()
    max_attempts = 4
    try:
        for attempt in range(max_attempts):
            email = input("Enter your email: ")
            password = getpass.getpass("Enter your password: ")

            cursor.execute('SELECT * FROM users WHERE (email,password) = (?,?)', (email,password))
            user = cursor.fetchone()
            if user is not None:
                print('Welcome, {}!'.format(user[1]))
                ## Call the appropriate method for the given role
                return user
            else:
                remaining_attempts = max_attempts - attempt
                print(f'Please enter a valid email and password, you are left with {remaining_attempts}')

        print('You have reached the maximum number of attempts to login, try again later.')
        return None

    except Exception as e:
        print('Error occurred while logging in, please try again later')
    finally:
        conn.close()

# =========================
# FARMER LOGIC
# =========================

def add_produce(farmer_id, cursor, conn):
    print("\n--- Add Produce ---")
    crop_name = input("Enter crop name: ").strip()

    if not crop_name:
        print("Crop name cannot be empty.")
        return

    try:
        quantity = int(input("Enter quantity: "))
        price = float(input("Enter price per unit (RWF): "))

        if quantity <= 0 or price <= 0:
            print("Quantity and price must be greater than 0.")
            return

        cursor.execute("""
            INSERT INTO inventory (farmer_id, crop_name, quantity, price, status)
            VALUES (?, ?, ?, ?, 'Stored')
        """, (farmer_id, crop_name, quantity, price))
        conn.commit()

        print(f"{crop_name} added successfully.")
    except ValueError:
        print("Invalid input. Enter valid numbers.")


def view_farmer_inventory(farmer_id, cursor):
    print("\n--- My Inventory ---")
    cursor.execute("""
        SELECT id, crop_name, quantity, price, status
        FROM inventory
        WHERE farmer_id = ?
    """, (farmer_id,))
    items = cursor.fetchall()

    if not items:
        print("You have no produce in inventory.")
        return

    print(f"{'Item ID':<10} | {'Crop':<15} | {'Quantity':<10} | {'Price':<12} | {'Status':<10}")
    print("-" * 70)
    for item in items:
        item_id, crop_name, quantity, price, status = item
        print(f"{item_id:<10} | {crop_name:<15} | {quantity:<10} | {price:<12.2f} | {status:<10}")


def list_produce(farmer_id, cursor, conn):
    view_farmer_inventory(farmer_id, cursor)
    try:
        item_id = int(input("\nEnter Item ID to list on market (or 0 to cancel): "))
        if item_id == 0:
            return

        cursor.execute("""
            SELECT id, quantity, status
            FROM inventory
            WHERE id = ? AND farmer_id = ?
        """, (item_id, farmer_id))
        item = cursor.fetchone()

        if not item:
            print("Item not found.")
            return

        _, quantity, status = item

        if quantity <= 0:
            print("Cannot list item with zero quantity.")
            return

        if status == "Listed":
            print("This item is already listed.")
            return

        cursor.execute("""
            UPDATE inventory
            SET status = 'Listed'
            WHERE id = ? AND farmer_id = ?
        """, (item_id, farmer_id))
        conn.commit()

        print("Produce listed successfully.")
    except ValueError:
        print("Invalid input.")


def update_produce(farmer_id, cursor, conn):
    view_farmer_inventory(farmer_id, cursor)
    try:
        item_id = int(input("\nEnter Item ID to update (or 0 to cancel): "))
        if item_id == 0:
            return

        cursor.execute("""
            SELECT crop_name, quantity, price
            FROM inventory
            WHERE id = ? AND farmer_id = ?
        """, (item_id, farmer_id))
        item = cursor.fetchone()

        if not item:
            print("Item not found.")
            return

        old_crop, old_qty, old_price = item

        new_crop = input(f"Enter new crop name [{old_crop}]: ").strip()
        qty_input = input(f"Enter new quantity [{old_qty}]: ").strip()
        price_input = input(f"Enter new price [{old_price}]: ").strip()

        crop_name = new_crop if new_crop else old_crop
        quantity = int(qty_input) if qty_input else old_qty
        price = float(price_input) if price_input else old_price

        if quantity < 0 or price < 0:
            print("Quantity and price cannot be negative.")
            return

        cursor.execute("""
            UPDATE inventory
            SET crop_name = ?, quantity = ?, price = ?
            WHERE id = ? AND farmer_id = ?
        """, (crop_name, quantity, price, item_id, farmer_id))
        conn.commit()

        print("Produce updated successfully.")
    except ValueError:
        print("Invalid input.")


def delete_produce(farmer_id, cursor, conn):
    view_farmer_inventory(farmer_id, cursor)
    try:
        item_id = int(input("\nEnter Item ID to delete (or 0 to cancel): "))
        if item_id == 0:
            return

        cursor.execute("""
            SELECT crop_name
            FROM inventory
            WHERE id = ? AND farmer_id = ?
        """, (item_id, farmer_id))
        item = cursor.fetchone()

        if not item:
            print("Item not found.")
            return

        confirm = input(f"Are you sure you want to delete '{item[0]}'? (Y/N): ").strip().upper()
        if confirm == 'Y':
            cursor.execute("""
                DELETE FROM inventory
                WHERE id = ? AND farmer_id = ?
            """, (item_id, farmer_id))
            conn.commit()
            print("Produce deleted successfully.")
        else:
            print("Delete cancelled.")
    except ValueError:
        print("Invalid input.")


def view_sales_history(farmer_id, cursor):
    print("\n--- Sales History ---")
    query = """
        SELECT transactions.id, inventory.crop_name, transactions.quantity, transactions.total_price
        FROM transactions
        JOIN inventory ON transactions.crop_id = inventory.id
        WHERE inventory.farmer_id = ?
    """
    cursor.execute(query, (farmer_id,))
    sales = cursor.fetchall()

    if not sales:
        print("No sales yet.")
        return

    print(f"{'Receipt ID':<12} | {'Crop':<15} | {'Qty Sold':<10} | {'Total Earned (RWF)':<20}")
    print("-" * 65)
    for sale in sales:
        receipt_id, crop_name, qty, total = sale
        print(f"{receipt_id:<12} | {crop_name:<15} | {qty:<10} | {total:<20.2f}")


def farmer_menu(farmer_id, cursor, conn):
    while True:
        print("\n=== FARMER DASHBOARD ===")
        print("1. Add Produce")
        print("2. View My Inventory")
        print("3. List Produce for Sale")
        print("4. Update Produce")
        print("5. Delete Produce")
        print("6. View Sales History")
        print("7. Logout")

        choice = input("Select an option (1-7): ").strip()

        if choice == '1':
            add_produce(farmer_id, cursor, conn)
        elif choice == '2':
            view_farmer_inventory(farmer_id, cursor)
        elif choice == '3':
            list_produce(farmer_id, cursor, conn)
        elif choice == '4':
            update_produce(farmer_id, cursor, conn)
        elif choice == '5':
            delete_produce(farmer_id, cursor, conn)
        elif choice == '6':
            view_sales_history(farmer_id, cursor)
        elif choice == '7':
            print("Logging out... Returning to Main Menu.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


# =========================
# BUYER LOGIC
# =========================

def view_market_board(cursor):
    print("\n--- Market Board ---")
    query = """
        SELECT inventory.id, users.name, inventory.crop_name, inventory.quantity, inventory.price
        FROM inventory
        JOIN users ON inventory.farmer_id = users.id
        WHERE inventory.status = 'Listed' AND inventory.quantity > 0
    """
    cursor.execute(query)
    crops = cursor.fetchall()
    
    if not crops:
        print("The market is currently empty. Check back later!")
        return

    print(f"{'Item ID':<10} | {'Farmer':<15} | {'Crop':<15} | {'Qty Available':<15} | {'Price (RWF)':<15}")
    print("-" * 75)
    for crop in crops:
        item_id, farmer_name, crop_name, quantity, price = crop
        print(f"{item_id:<10} | {farmer_name:<15} | {crop_name:<15} | {quantity:<15} | {price:<15.2f}")

def purchase_produce(buyer_id, cursor, conn):
    view_market_board(cursor) 
    try:
        item_id = int(input("\nEnter the Item ID you want to purchase (or 0 to cancel): "))

        if item_id == 0: return

        if item_id == 0:
            return

        buy_qty = int(input("Enter the quantity you want to buy: "))
        if buy_qty <= 0:
            print("Quantity must be greater than 0.")
            return
        
        cursor.execute("SELECT quantity, price FROM inventory WHERE id = ? AND status = 'Listed'", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            print("Error: Item not found or not available for sale.")
            return
            
        available_qty, price = item
        if buy_qty > available_qty:
            print(f"Error: Only {available_qty} available.")
            return
            
        total_price = buy_qty * price
        print(f"\nTotal cost for {buy_qty} units is {total_price:.2f} RWF.")
        confirm = input("Confirm purchase? (Y/N): ").strip().upper()
        
        if confirm == 'Y':
            new_qty = available_qty - buy_qty
            cursor.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, item_id))

            if new_qty == 0:
                cursor.execute("UPDATE inventory SET status = 'Stored' WHERE id = ?", (item_id,))


            cursor.execute("""
                INSERT INTO transactions (buyer_id, crop_id, quantity, total_price)
                VALUES (?, ?, ?, ?)
            """, (buyer_id, item_id, buy_qty, total_price))
            conn.commit()
            print("Purchase successful! Receipt saved to your history.")
        else:
            print("Purchase cancelled.")
    except ValueError:
        print("Invalid input. Please enter whole numbers.")

def view_history(buyer_id, cursor):
    print("\n--- Purchase History ---")
    query = """
        SELECT transactions.id, inventory.crop_name, transactions.quantity, transactions.total_price
        FROM transactions
        JOIN inventory ON transactions.crop_id = inventory.id
        WHERE transactions.buyer_id = ?
    """
    cursor.execute(query, (buyer_id,))
    history = cursor.fetchall()
    
    if not history:
        print("You haven't made any purchases yet.")
        return        
    print(f"{'Receipt ID':<15} | {'Crop':<15} | {'Qty Bought':<15} | {'Total Paid (RWF)':<15}")
    print("-" * 65)
    for row in history:
        receipt_id, crop_name, qty, total = row
        print(f"{receipt_id:<15} | {crop_name:<15} | {qty:<15} | {total:<15.2f}")

def buyer_menu(buyer_id, cursor, conn):
    while True:
        print("\n=== BUYER DASHBOARD ===")
        print("1. View Market Board")
        print("2. Purchase Produce")
        print("3. View History")
        print("4. Logout")
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            view_market_board(cursor)
        elif choice == '2':
            purchase_produce(buyer_id, cursor, conn)
        elif choice == '3':
            view_history(buyer_id, cursor)
        elif choice == '4':
            print("Logging out... Returning to Main Menu.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


# =========================
# MAIN APPLICATION LOOP
# =========================

def main():
    # Initialize the db on startup
    init_db()
    
    print("\n" + "="*50)
    print(" Welcome to FarmLink - The Market Connector! ")
    print("="*50)

    while True:
        print("\n=== MAIN MENU ===")
        print("1. Login")
        print("2. Register New User")
        print("3. Exit System")

        choice = input("Select an option (1-3): ").strip()

        if choice == '1':
            # Call login function
            user = login()
            
            if user:
                # user is a tuple from the DB: (id, name, email, password, role)
                user_id = user[0]
                user_name = user[1]
                role = user[4]

                print(f"\n Login successful! Welcome back, {user_name}.")

                # Open db connection for buyer and farmer logic
                conn = sqlite3.connect("farmlink.db")
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()

                # Link to correct dashboard based on role
                if role == "Farmer":
                    farmer_menu(user_id, cursor, conn)
                elif role == "Buyer":
                    buyer_menu(user_id, cursor, conn)
                
                # Close connection when user logout of their dashboard
                conn.close()

        elif choice == '2':
            # Call signup function
            signup()

        elif choice == '3':
            print("\n Exiting FarmLink..... Goodbye!")
            sys.exit()

        else:
            print("Oops invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
     try:

        main()

     except KeyboardInterrupt:
        print("\n\n Exiting FarmLink...... Goodbye!")
        sys.exit(0)
