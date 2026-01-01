import streamlit as st
from datetime import date
from db import insert_tx, fetch_df, update_amount  # 你 db.py 需要有這三個

# -----------------------
# 設定：帳戶 / 類別 / 付款方式
# -----------------------
CATEGORIES = {
    "常弘服裝": ["春美的工錢", "阿霞的工錢", "江代工的工錢", "整燙", "印花", "徽章", "彩帶", "鬆緊帶", "滾條", "其它"],
    "個人開銷": ["早餐", "午餐", "晚餐", "其它"],
}
PAYMENTS_PERSONAL = ["信用卡", "現金"]

# -----------------------
# Page UI
# -----------------------
st.title("記帳")

# 若沒選帳戶，導回首頁
if "account" not in st.session_state:
    st.warning("請先回首頁選擇帳戶")
    st.stop()

account = st.session_state["account"]

# -----------------------
# 新增支出
# -----------------------
st.subheader(f"新增支出（目前帳戶：{account}）")

with st.form("add_tx", clear_on_submit=True):
    tx_date = st.date_input("日期", value=date.today())
    category = st.selectbox("類別", CATEGORIES[account])
    amount = st.number_input("金額", min_value=1.0, step=10.0, format="%.2f")

    payment_method = None
    if account == "個人開銷":
        payment_method = st.selectbox("支付方式", PAYMENTS_PERSONAL)
    else:
        st.caption("常弘服裝：支付方式可不填")

    note = st.text_input("備註（可空）")

    # ✅ 同一排：左「記一筆」右「回到主頁」
    col_left, col_right = st.columns([3, 1])
    with col_left:
        submit_add = st.form_submit_button("記一筆", use_container_width=True)
    with col_right:
        go_home = st.form_submit_button("🏠 回到主頁", use_container_width=True)

# 按「回到主頁」
if go_home:
    st.switch_page("pages/0_首頁.py")

# 按「記一筆」
if submit_add:
    if amount <= 0:
        st.error("金額必須大於 0")
    else:
        insert_tx(
            account=account,
            category=category,
            amount=float(amount),
            tx_date=tx_date,
            payment_method=payment_method,
            note=note
        )
        st.success("已記錄 ✅")
        st.rerun()

# -----------------------
# 修改金額（最近 20 筆）
# -----------------------
st.markdown("---")
st.subheader("修改金額（最近 20 筆）")

df = fetch_df("account = ?", (account,))
df_recent = df.head(20).copy() if df is not None else None

if df_recent is None or df_recent.empty:
    st.info("目前沒有可修改的紀錄")
else:
    # 顯示最近 20 筆（讓你能對照）
    show_cols = ["id", "tx_date", "category", "amount", "payment_method", "note"]
    show_cols = [c for c in show_cols if c in df_recent.columns]
    st.dataframe(df_recent[show_cols], use_container_width=True)

    # 用 ID 選一筆
    tx_id = st.selectbox("選擇要修改的紀錄 ID", df_recent["id"].tolist())

    row = df_recent[df_recent["id"] == tx_id].iloc[0]
    old_amount = float(row["amount"])

    new_amount = st.number_input(
        "新的金額",
        min_value=1.0,
        step=10.0,
        value=old_amount,
        format="%.2f"
    )

    colA, colB = st.columns(2)
    with colA:
        st.caption(f"原本金額：{old_amount:.2f}")
    with colB:
        st.caption(f"修改後：{new_amount:.2f}")

    col_save, col_home2 = st.columns([3, 1])
    with col_save:
        if st.button("儲存金額修改", use_container_width=True):
            update_amount(int(tx_id), float(new_amount))
            st.success(f"已更新 ✅  (# {tx_id}) {old_amount:.2f} → {new_amount:.2f}")
            st.rerun()

    with col_home2:
        if st.button("🏠 回到主頁", use_container_width=True):
            st.switch_page("pages/0_首頁.py")
