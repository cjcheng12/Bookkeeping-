
import streamlit as st
from datetime import date
from db import insert_tx

st.title("記帳")

if "account" not in st.session_state:
    st.warning("請先回首頁選擇帳戶")
    st.stop()

account = st.session_state["account"]

CATEGORIES = {
    "常弘服裝": ["春美的工錢","阿霞的工錢","江代工的工錢","整燙","印花","徽章","彩帶","鬆緊帶","滾條","其它"],
    "個人開銷": ["早餐","午餐","晚餐","其它"]  # ✅ 信用卡改成支付方式
}
PAYMENTS = ["信用卡", "現金"]

with st.form("add_tx", clear_on_submit=True):
    tx_date = st.date_input("日期", value=date.today())
    category = st.selectbox("類別", CATEGORIES[account])
    amount = st.number_input("金額", min_value=1.0, step=10.0, format="%.2f")

    payment_method = None
    if account == "個人開銷":
        payment_method = st.selectbox("支付方式", PAYMENTS)
    else:
        st.caption("常弘服裝：支付方式可不填")

    note = st.text_input("備註（可空）", placeholder="例如：店名、案號、哪一張單…")
    ok = st.form_submit_button("記一筆")

if ok:
    if amount <= 0:
        st.error("金額必須大於 0")
    else:
        insert_tx(account, category, amount, tx_date, payment_method, note)
        pm = payment_method if payment_method else "-"
        st.success(f"已記錄：{account} / {category} / {amount:.2f} / {pm} / {tx_date}")
