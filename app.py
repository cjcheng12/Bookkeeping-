import streamlit as st

st.set_page_config(
    page_title="常弘記帳",
    page_icon="💰",
    layout="wide"
)

# Left sidebar selection
st.sidebar.header("設定")
account = st.sidebar.selectbox(
    "你要記錄哪一個帳戶呢？",
    ["常弘服裝", "個人開銷"]
)
st.session_state["account"] = account

# Main page content
st.title("現金流記帳程式")
st.write(f"目前帳戶：**{account}**")
st.caption("請從左側選單進入：記帳 / 報表")
