#  FarmLink CLI

**A terminal-based post-harvest and direct market connector for smallholder farmers in Rwanda.**

FarmLink CLI is a lightweight, menu-driven Python application designed to empower smallscale farmers. By providing a digital inventory tracker and a direct-to-buyer market board, FarmLink cuts out exploitative middlemen and helps reduce post-harvest food waste.

---

##  The Problem We Are Solving
Smallscale farmers experience high post-harvest losses (up to 30-40% of yields) due to poor tracking and a lack of direct access to buyers. Furthermore, farmers rely on middlemen who purchase produce at below-market value, drastically reducing the farmer's profit margin. 

**FarmLink** solves this by providing:
1. A digital inventory tracker to manage stored produce and reduce waste.
2. A direct peer-to-peer market board to ensure farmers get fair prices (calculated in RWF) directly from consumers.

##  Features
* **Secure Authentication:** Registration and login system featuring Regex email validation and hidden password masking (`getpass`).
* **Dynamic Routing:** Users are automatically routed to specific dashboards based on their role (`Farmer` or `Buyer`).
* **Farmer Dashboard:** Full CRUD functionality to add, view, update, list, and delete produce, plus a sales history tracker.
* **Buyer Dashboard:** Browse a live market board of all listed crops, complete purchases, automatically deduct inventory, and view detailed receipts.
* **Error Handling:** Built-in safeguards (`try/except` blocks) to prevent application crashes from invalid inputs and smooth `Ctrl+C` exit handling.

## Tech Stack
* **Language:** Python 3
* **Database:** SQLite3 (Built-in relational database using `PRAGMA foreign_keys = ON`)
* **Architecture:** Command Line Interface (CLI)

---

##  How to Clone and Run (Local Setup)
This application is designed to be incredibly smooth to run. It requires **no external database servers** and **no third-party libraries**. Everything runs natively in Python!

### Prerequisites
* Ensure you have [Python 3](https://www.python.org/downloads/) installed on your machine.

### Step-by-Step Instructions
**1. Clone the repository:**
```bash
git clone https://github.com/s-chukwu/Python-Group23-Farmlink

**2. Navigate into the project folder:**
```bash
cd Python-Group23-Farmlink

**3. Run the application:**
```bash
python3 farmlink.py

Database Note: You do not need to configure or install a database. The very first time you run the script, init_db() will automatically create a farmlink.db file in your folder with all the required tables and schema perfectly configured.

### Database Architecture
The application uses a localized SQLite relational database with three connected tables:
* Users Table: Stores user credentials, emails, and roles (Farmer or Buyer).
* Inventory Table: Stores crop data, quantities, prices, and status (Stored or Listed). Linked to the Farmer via Foreign Key.
* Transactions Table: Stores purchase receipts, total costs, and quantities bought. Linked to both the Buyer and the Inventory via Foreign Keys.


### Team Members & Contributions
This project was collaboratively built by Group 23:
Kelly Sangwe - Database Architect ( Designed SQL schemas and init_db() )
Magnificat Marie Augusta Umutesi - Authentication Engineer (Built signup() and login() with Regex/Getpass)
Batsinda Benoit - Farmer Logic Developer (Built supply-side CRUD operations)
Innocente Mutabazi Umuhuza - Buyer Logic Developer (Built demand-side JOIN queries and transaction math)
Sochukwuma Chukwu - System Integrator (Main application loop, role routing, exception handling, and GitHub management)
