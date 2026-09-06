import os
import sqlite3
from datetime import date


class Expenses:
    def __init__(self):
        self.db_dir = os.path.join(os.path.dirname(__file__), "data") # Creates the database directory within the same folder.
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        # Create the database file path safely.
        self.db_path = os.path.join(self.db_dir, "userdata.db")
        self.db = sqlite3.connect(self.db_path) # Opens the database
        self.cursor = self.db.cursor()
        self.create_table()
        self.currency = self.get_currency()
        self.default_start = date.today().replace(day=1).isoformat() # Start of the month
        self.default_end = date.today().isoformat() # Today
        
    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trans_date TEXT NOT NULL,
                trans_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT)
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS options(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            currency TEXT NOT NULL DEFAULT 'INR')
        """)
        self.cursor.execute("""
            INSERT INTO options (currency)
            SELECT 'INR' 
            WHERE NOT EXISTS (SELECT 1 FROM options)
        """)
        self.db.commit()

    def get_currency(self): # Gets the currency type as set by the user.
        return self.cursor.execute("""
            SELECT (currency) FROM options
        """).fetchone()[0]

    def set_currency(self, value): # Helps the user change the currency. Redraws the application with new currency.
        self.cursor.execute("""
            UPDATE options SET currency = ?
        """, (value,)
        )
        self.db.commit()

    def data_generator(self, start=None, end=None):
        if not start:
            start = self.default_start
        if not end:
            end = self.default_end
        self.cursor.execute("""
            SELECT id, trans_date, trans_type, category, amount, description 
            FROM transactions 
            WHERE trans_date >= ? 
            AND trans_date <= ?
            ORDER BY trans_date""", (start, end))
        yield from self.cursor

    def get_transaction(self, id): # Gets the transaction details for a specific transaction with its id.
        return self.cursor.execute("""
            SELECT * FROM transactions WHERE id = ?
        """, (id,)).fetchone()

    def save_transaction(self, transaction): #transaction is a tuple sent from Trans_Form
        self.cursor.execute("""
            INSERT INTO transactions (trans_date, trans_type, category, amount,
                            description) VALUES (?, ?, ?, ?, ?)""", 
                            transaction)
        self.db.commit()

    def update_transaction(self, transaction):
        self.cursor.execute("""
            UPDATE transactions SET
            trans_date = ?,
            trans_type = ?,
            category = ?,
            amount = ?, 
            description = ?
            WHERE id = ?
            """, transaction                        
            )
        self.db.commit()

    # Delete the transaction, especially when invoked from the delete button on the tracker.
    def del_transaction(self, id):
        self.cursor.execute("""
            DELETE FROM transactions WHERE id = ?
            """, (id,))
        self.db.commit()
                         
    def summary_generator(self, start=None, end=None):
        summary = {}
        summary["Balance"], summary["Expense"], summary["Income"] = 0,0,0
        if start is None:
            start = self.default_start
        if end is None:
            end = self.default_end
        summary_data = self.cursor.execute("""
            SELECT * FROM transactions WHERE trans_date >= ? AND trans_date <= ?
            ORDER BY trans_date
                            """, (start, end)).fetchall()
        for item in summary_data:
            if item[2] == "Income":
                summary["Balance"] += item[4]
                summary["Income"] += item[4]
            else:
                summary["Balance"] -= item[4]
                summary["Expense"] += item[4]
        return summary