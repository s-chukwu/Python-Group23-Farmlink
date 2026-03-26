import email
import getpass
import re
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
            if not userExists(conn, email):
                break
            print('Account already exists, please enter another one or login')

        # Obscure password while entering it
        password = getpass.getpass("Enter your password: ")

        # get valid role
        role=get_valid_role()
        cursor.execute('INSERT INTO users (name, email, password, role) values (?, ?, ?, ?)', (name, email, password, role))
        conn.commit()
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
            role_choice = int(input("Enter a number that matches who you are registering as: \n 1. Farmer \n 2. Buyer"))
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
                print('Welcome, {}!'.format(user[0]))
                ## Call the appropriate method for the given role
                return
            else:
                remaining_attempts = max_attempts - attempt
                print(f'Please enter a valid email and password, you are left with {remaining_attempts}')

        print('You have reached the maximum number of attempts to login, try again later.')
        return None

    except Exception as e:
        print('Error occurred while logging in, please try again later')
    finally:
        conn.close()

