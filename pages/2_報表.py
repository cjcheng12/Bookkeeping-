import streamlit as st
from datetime import date
from db import fetch_df

st.title("報表")

today = date.today()

def month_range(year: int, month: int):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end

def year_range(year: int):
    return date(year, 1, 1), date(year + 1, 1, 1)

tab1, tab2 = st.tabs(["本月", "本年"])

with tab1:
    y = st.number_input("年份", value=today.year, step=1, key="m_y")
    m = st.number_input("月份", min_value=1, max_value=12, value=today.month, step=1, key="m_m")
    start, end = month_range(int(y), int(m))

    df = fetch_df("tx_date >= ? AND tx_date < ?", (start.isoformat(), end.isoformat()))
    st.caption(f"期間：{start} ～ {end}")

    if df.empty:
        st.info("本月無資料")
    else:
        st.subheader("本月總支出（依帳戶）")
        st.dataframe(df.groupby("account")["amount"].sum().reset_index(), use_container_width=True)

        st.subheader("本月類別加總（依帳戶）")
        st.dataframe(df.groupby(["account","category"])["amount"].sum().reset_index(), use_container_width=True)

        st.subheader("個人開銷：支付方式加總")
        p = df[df["account"] == "個人開銷"]
        if p.empty:
            st.caption("本月沒有個人開銷")
        else:
            st.dataframe(p.groupby("payment_method")["amount"].sum().reset_index(), use_container_width=True)

            st.subheader("個人開銷：信用卡都花在哪些類別")
            cc = p[p["payment_method"] == "信用卡"]
            if cc.empty:
                st.caption("本月信用卡支出為 0")
            else:
                st.dataframe(cc.groupby("category")["amount"].sum().reset_index(), use_container_width=True)

with tab2:
    y2 = st.number_input("年份", value=today.year, step=1, key="y_y")
    start, end = year_range(int(y2))

    df = fetch_df("tx_date >= ? AND tx_date < ?", (start.isoformat(), end.isoformat()))
    st.caption(f"期間：{start} ～ {end}")

    if df.empty:
        st.info("本年無資料")
    else:
        st.subheader("本年總支出（依帳戶）")
        st.dataframe(df.groupby("account")["amount"].sum().reset_index(), use_container_width=True)

        st.subheader("本年類別加總（依帳戶）")
        st.dataframe(df.groupby(["account","category"])["amount"].sum().reset_index(), use_container_width=True)

        st.subheader("個人開銷：本年支付方式加總")
        p = df[df["account"] == "個人開銷"]
        if p.empty:
            st.caption("本年沒有個人開銷")
        else:
            st.dataframe(p.groupby("payment_method")["amount"].sum().reset_index(), use_container_width=True)

