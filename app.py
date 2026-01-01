import streamlit as st

st.set_page_config(
    page_title="常弘記帳",
    page_icon="💰",
    layout="wide"
)

# ---- Title ----
st.title("現金流記帳程式")
st.write("")
st.write("")

# ---- Centered buttons ----
left, center, right = st.columns([1, 2, 1])

with center:
    st.subheader("你要記錄哪一個帳戶呢？")
    st.write("")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🏭 常弘服裝", use_container_width=True):
            st.session_state["account"] = "常弘服裝
