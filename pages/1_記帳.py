import streamlit as st
from datetime import date

st.title("記帳")

if "account" not in st.session_state:
    st.warning("請先回首頁選擇帳戶")
    st.stop()

account = st.session_state["account"]

CATEGORIES = {
    "常弘服裝": ["春美的工錢","阿霞的工錢","江代工的工錢","整燙","印花","徽章","彩帶","鬆緊帶","滾條","其它"],
    "個人開銷": ["早餐","午餐","晚餐","其它"]
}

PAYMENTS = ["信用卡", "現金"]

with st.form("add"):
    tx_date = st.date_input("日期", value=date.today())
    category = st.selectbox("類別", CATEGORIES[account])
    amount = st.number_input("金額", min_value=1.0, step=10.0)

    payment = None
    if account == "個人開銷":
        payment = st.selectbox("支付方式", PAYMENTS)

    note = st.text_input("備註（可空）")
    ok = st.form_submit_button("記一筆")

if ok:
    st.success("（下一步會接資料庫）")
