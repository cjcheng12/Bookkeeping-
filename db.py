import sqlite3
from datetime import date
import pandas as pd

DB_PATH = "cashflow.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL CHECK(amount > 0),
        tx_date TEXT NOT NULL,
        payment_method TEXT,
        note TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_tx(account: str, category: str, amount: float, tx_date: date, payment_method: str | None, note: str | None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions (account, category, amount, tx_date, payment_method, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        account, category, float(amount), tx_date.isoformat(),
        payment_method if payment_method else None,
        (note or "").strip() or None
    ))
    conn.commit()
    conn.close()

def fetch_df(where_sql: str = "", params: tuple = ()):
    conn = get_conn()
    q = "SELECT id, account, category, amount, tx_date, payment_method, note FROM transactions"
    if where_sql:
        q += " WHERE " + where_sql
    q += " ORDER BY tx_date DESC, id DESC"
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    if not df.empty:
        df["tx_date"] = pd.to_datetime(df["tx_date"]).dt.date
    return df

        
      
    
