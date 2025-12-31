import sqlite3
from datetime import date
import pandas as pd
import streamlit as st

DB_PATH = "cashflow.db"

ACCOUNTS = ["常弘服裝", "個人開銷"]

CATEGORIES = {
    "常弘服裝": ["春美的工錢", "阿霞的工錢", "江代工的工錢", "整燙", "印花", "徽章", "彩帶", "鬆緊帶", "滾條", "其它"],
    # ✅ 個人開銷：拿掉「信用卡」當類別
    "個人開銷": ["早餐", "午餐", "晚餐", "其它"],
}

PAYMENT_METHODS_PERSONAL = ["信用卡", "現金"]  # 你說大多用信用卡

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
        payment_method TEXT,     -- ✅ 新增：支付方式（個人開銷會用到）
        note TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_tx(account: str, category: str, amount: float, tx_date: date, payment_method: str | None, note: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO transactions (account, category, amount, tx_date, payment_method, note)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            account,
            category,
            float(amount),
            tx_date.isoformat(),
            payment_method if payment_method else None,
            note.strip() if note else None
        )
    )
    conn.commit()
    conn.close()

def fetch_df(where_sql: str = "", params: tuple = ()):
    conn = get_conn()
    query = "SELECT id, account, category, amount, tx_date, payment_method, note FROM transactions"
    if where_sql:
        query += " WHERE " + where_sql
    query += " ORDER BY tx_date DESC, id DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    if not df.empty:
        df["tx_date"] = pd.to_datetime(df["tx_date"]).dt.date
    return df

def month_range(year: int, month: int):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end

def year_range(year: int):
    return date(year, 1, 1), date(year + 1, 1, 1)

def sum_by(df: pd.DataFrame, cols: list[str]):
    if df.empty:
        return df
    return (
        df.groupby(cols, as_index=False)["amount"]
          .sum()
          .sort_values("amount", ascending=False)
    )

# ---------------- UI ----------------
st.set_page_config(page_title="現金流記帳", layout="wide")
init_db()

st.title("現金流記帳程式")

st.subheader("你要記錄哪一個帳戶呢？")
account = st.selectbox("選擇帳戶", ACCOUNTS)

st.markdown("---")
st.header(f"新增支出：{account}")

with st.form("add_tx_form", clear_on_submit=True):
    cols = st.columns([2, 2, 2, 2, 4])
    with cols[0]:
        tx_date = st.date_input("日期", value=date.today())
    with cols[1]:
        category = st.selectbox("類別", CATEGORIES[account])
    with cols[2]:
        amount = st.number_input("金額", min_value=0.0, step=10.0, format="%.2f")
    with cols[3]:
        payment_method = None
        if account == "個人開銷":
            payment_method = st.selectbox("支付方式", PAYMENT_METHODS_PERSONAL)
        else:
            st.caption("支付方式：不需要")
    with cols[4]:
        note = st.text_input("備註（可空）", placeholder="例如：店名、案號、結帳方式細節…")

    submitted = st.form_submit_button("記一筆")

if submitted:
    if amount <= 0:
        st.error("金額必須大於 0")
    else:
        insert_tx(account, category, amount, tx_date, payment_method, note)
        pm_text = payment_method if payment_method else "-"
        st.success(f"已記錄：{account} / {category} / {amount:.2f} / {pm_text} / {tx_date.isoformat()}")

st.markdown("---")
st.header("查詢報表")

today = date.today()
default_year = today.year
default_month = today.month

tab1, tab2, tab3 = st.tabs(["本月支出", "本年支出", "全部明細"])

with tab1:
    y = st.number_input("年份", min_value=2000, max_value=2100, value=default_year, step=1, key="m_year")
    m = st.number_input("月份", min_value=1, max_value=12, value=default_month, step=1, key="m_month")
    start, end = month_range(int(y), int(m))

    df = fetch_df("tx_date >= ? AND tx_date < ?", (start.isoformat(), end.isoformat()))
    st.write(f"期間：{start} ~ {end - pd.Timedelta(days=1)}")

    colA, colB = st.columns(2)
    with colA:
        st.subheader("本月總支出（依帳戶）")
        if df.empty:
            st.info("本月尚無資料")
        else:
            st.dataframe(sum_by(df, ["account"]), use_container_width=True)

    with colB:
        st.subheader("本月各類別加總（依帳戶）")
        if df.empty:
            st.info("本月尚無資料")
        else:
            st.dataframe(sum_by(df, ["account", "category"]), use_container_width=True)

    # ✅ 個人開銷：支付方式報表
    st.markdown("### 個人開銷：本月支付方式分析")
    df_p = df[df["account"] == "個人開銷"].copy()
    if df_p.empty:
        st.caption("本月沒有個人開銷資料")
    else:
        left, right = st.columns(2)
        with left:
            st.write("依支付方式加總")
            st.dataframe(sum_by(df_p, ["payment_method"]), use_container_width=True)
        with right:
            st.write("信用卡都花在哪些類別")
            df_cc = df_p[df_p["payment_method"] == "信用卡"]
            if df_cc.empty:
                st.caption("本月信用卡支出為 0")
            else:
                st.dataframe(sum_by(df_cc, ["category"]), use_container_width=True)

with tab2:
    y2 = st.number_input("年份", min_value=2000, max_value=2100, value=default_year, step=1, key="y_year")
    start, end = year_range(int(y2))
    df = fetch_df("tx_date >= ? AND tx_date < ?", (start.isoformat(), end.isoformat()))
    st.write(f"期間：{start} ~ {end - pd.Timedelta(days=1)}")

    colA, colB = st.columns(2)
    with colA:
        st.subheader("本年總支出（依帳戶）")
        if df.empty:
            st.info("本年尚無資料")
        else:
            st.dataframe(sum_by(df, ["account"]), use_container_width=True)

    with colB:
        st.subheader("本年各類別加總（依帳戶）")
        if df.empty:
            st.info("本年尚無資料")
        else:
            st.dataframe(sum_by(df, ["account", "category"]), use_container_width=True)

    st.markdown("### 個人開銷：本年支付方式分析")
    df_p = df[df["account"] == "個人開銷"].copy()
    if df_p.empty:
        st.caption("本年沒有個人開銷資料")
    else:
        st.dataframe(sum_by(df_p, ["payment_method"]), use_container_width=True)

with tab3:
    df_all = fetch_df()
    st.subheader("全部明細")
    if df_all.empty:
        st.info("目前沒有任何記錄")
    else:
        st.dataframe(df_all, use_container_width=True)
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button("下載 CSV", data=csv, file_name="cashflow_transactions.csv", mime="text/csv")
