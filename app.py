import streamlit as st
from db import init_db

st.set_page_config(
    page_title="現金流記帳",  # ← 這就是 App 名稱
    layout="wide"
)

init_db()

st.title("現金流記帳程式")

account = st.selectbox("你要記錄哪一個帳戶呢？", ["常弘服裝", "個人開銷"])
st.session_state["account"] = account

st.success(f"目前帳戶：{account}")
st.caption("請從左側選單進入：記帳 / 報表")
