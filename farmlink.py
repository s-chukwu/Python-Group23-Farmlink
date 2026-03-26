import sqlite3

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



# Buyer's logic 

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


