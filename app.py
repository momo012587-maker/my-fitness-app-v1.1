import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

# 設定網頁標題
st.set_page_config(page_title="飲食與體重趨勢紀錄")
st.title("飲食與體重趨勢紀錄")

# ==========================================
# 1. 計算 TDEE 區塊
# ==========================================
st.header("1. 計算 TDEE (每日總熱量消耗)")

col1, col2 = st.columns(2)
with col1:
    bmr = st.number_input("基礎代謝率 (BMR):", min_value=0, value=1600, step=10)

with col2:
    activity_options = {
        "久坐 (幾乎不運動)": 1.2,
        "輕度活動 (每週運動 1-3 天)": 1.375,
        "中度活動 (每週運動 3-5 天)": 1.55,
        "高度活動 (每週運動 6-7 天)": 1.725,
        "極度活動 (勞力工作或高強度訓練)": 1.9
    }
    activity_text = st.selectbox("平常活動狀態:", list(activity_options.keys()))

# 計算並顯示 TDEE
current_tdee = bmr * activity_options[activity_text]
st.markdown(f"**目前 TDEE:** :red[{round(current_tdee)}] **大卡**")
st.divider()

# ==========================================
# 2. 食物熱量與營養素區塊
# ==========================================
st.header("2. 食物熱量與營養素")
st.caption("輸入部分數值後，點擊「自動計算缺項」按鈕推算剩餘欄位 (碳水/蛋白質 1g=4大卡, 脂肪 1g=9大卡)")

# 初始化暫存變數 (Session State) 以便保留輸入框的數值
for key in ['cal', 'p', 'c', 'f']:
    if key not in st.session_state:
        st.session_state[key] = None

def auto_fill_macros():
    cal = st.session_state.cal
    p = st.session_state.p
    c = st.session_state.c
    f = st.session_state.f
    
    # 情況 A: 填了三大營養素，推算總熱量
    if cal is None and None not in (p, c, f):
        st.session_state.cal = float(round(p * 4 + c * 4 + f * 9, 1))
    
    # 情況 B: 填了總熱量及其中兩項營養素，推算剩下的那一項
    elif cal is not None:
        if p is None and None not in (c, f):
            st.session_state.p = float(max(0.0, round((cal - c * 4 - f * 9) / 4, 1)))
        elif c is None and None not in (p, f):
            st.session_state.c = float(max(0.0, round((cal - p * 4 - f * 9) / 4, 1)))
        elif f is None and None not in (p, c):
            st.session_state.f = float(max(0.0, round((cal - p * 4 - c * 4) / 9, 1)))

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1: st.number_input("總熱量 (kcal)", key="cal", value=None)
with col_m2: st.number_input("蛋白質 (g)", key="p", value=None)
with col_m3: st.number_input("碳水化合物 (g)", key="c", value=None)
with col_m4: st.number_input("脂肪 (g)", key="f", value=None)

st.button("自動計算缺項", on_click=auto_fill_macros, type="primary")

weight = st.number_input("目前體重 (kg):", min_value=30.0, value=70.0, step=0.1)
st.divider()

# ==========================================
# 3. 趨勢圖區塊
# ==========================================
st.header("3. 體重趨勢圖 (未來 30 天模擬)")

if st.button("產生 / 更新圖表", type="primary"):
    cal = st.session_state.cal
    if cal is None:
        st.error("請確保「總熱量」已填寫，才能計算赤字與模擬圖表。")
    elif current_tdee <= 0:
        st.error("請確認 TDEE 計算數值正常。")
    else:
        fig, ax = plt.subplots(figsize=(8, 4))
        
        days = 30
        today = datetime.date.today()
        dates = [today + datetime.timedelta(days=i) for i in range(days)]
        
        # 理論赤字：標準每天 -500 大卡 (約每週減脂 0.5kg)
        theoretical_deficit = 500
        theoretical_loss_per_day = theoretical_deficit / 7700
        theoretical_weights = [weight - (theoretical_loss_per_day * i) for i in range(days)]

        # 實際模擬赤字：依照目前 TDEE 減去輸入的總攝取熱量
        actual_deficit = current_tdee - cal
        actual_loss_per_day = actual_deficit / 7700
        actual_weights = [weight - (actual_loss_per_day * i) for i in range(days)]

        # 繪製圖表 (無滑鼠懸停功能)
        ax.plot(dates, theoretical_weights, linestyle='--', color='blue', label='理論目標 (每日 -500kcal)')
        ax.plot(dates, actual_weights, linestyle='-', color='red', label=f'實際模擬 (目前赤字 {round(actual_deficit)}kcal)')

        # 設定 X 軸為日期格式
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        fig.autofmt_xdate()

        ax.set_title("未來 30 天體重下降模擬")
        ax.set_ylabel("體重 (kg)")
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)

        # 輸出圖表到網頁上
        st.pyplot(fig)
