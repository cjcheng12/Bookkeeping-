import streamlit as st

st.set_page_config(
    page_title="常弘記帳",
    page_icon="💰",
    layout="wide"
)

st.title("現金流記帳程式")
st.write("")
st.write("")

left, center, right = st.columns([1, 2, 1])

with center:
    st.subheader("你要記錄哪一個帳戶呢？")
    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏭 常弘服裝", use_container_width=True):
            st.session_state["account"] = "常弘服裝"
            st.switch_page("pages/1_記帳.py")

    with col2:
        if st.button("👤 個人開銷", use_container_width=True):
            st.session_state["account"] = "個人開銷"
            st.switch_page("pages/1_記帳.py")
