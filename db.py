import sqlite3
from datetime import date
import pandas as pd

DB_PATH = "cashflow.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
def insert_tx(account, category, amount, tx_date, payment_method, note):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions
        (account, category, amount, tx_date, payment_method, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        account,
        category,
        float(amount),
        tx_date.isoformat(),
        payment_method,
        (note or "").strip() or None
    ))
    conn.commit()
    conn.close()
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # 1. 確保 table 存在（新資料庫）
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

    # 2. 讀取現有欄位（舊資料庫升級）
    cur.execute("PRAGMA table_info(transactions)")
    existing_columns = [row[1] for row in cur.fetchall()]

    if "payment_method" not in existing_columns:
        cur.execute("ALTER TABLE transactions ADD COLUMN payment_method TEXT")

    if "note" not in existing_columns:
        cur.execute("ALTER TABLE transactions ADD COLUMN note TEXT")

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
def update_amount(tx_id: int, new_amount: float):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE transactions SET amount = ? WHERE id = ?",
        (float(new_amount), int(tx_id))
    )
    conn.commit()
    conn.close()
init_db()
        
      
    
