import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="喵！全能減重戰鬥儀", page_icon="🐾", layout="wide")

if 'c_w' not in st.session_state: st.session_state.c_w = 0.0
if 'c_bf' not in st.session_state: st.session_state.c_bf = 0.0

st.title("🐾 喵！全能減重戰鬥星艦 (MVP 測試版)")
st.write("輸入你的專屬數據，喚醒貓咪教練為你量身打造的減重計畫喵！")

tab1, tab2, tab3, tab4 = st.tabs(["📊 1&2. InBody 與目標", "📸 3. AI 飲食", "🏃‍♂️ 4. 運動處方", "📈 7. 成效分析"])

# --- Tab 1 ---
with tab1:
    col_in, col_tgt = st.columns(2)
    with col_in:
        st.subheader("📑 Step 1: 獲取目前身體數據")
        if st.button("📸 模擬上傳 InBody 報告 (自動填入)"):
            st.session_state.c_w = 78.5
            st.session_state.c_bf = 22.5
            st.success("✅ AI 讀取成功！")
        
        c_w = st.number_input("目前體重 (kg)", value=st.session_state.c_w, step=0.1)
        c_bf = st.number_input("目前體脂 (%)", value=st.session_state.c_bf, step=0.1)
        
    with col_tgt:
        st.subheader("🎯 Step 2: 你的理想目標")
        t_w = st.number_input("目標體重 (kg)", value=0.0, step=0.1)
        t_bf = st.number_input("目標體脂 (%)", value=0.0, step=0.1)
        weeks = st.slider("預計達成時間 (週)", min_value=4, max_value=24, value=12)

    st.divider()
    if c_w > 0 and t_w > 0:
        if c_w > t_w:
            total_loss = c_w - t_w
            weekly_loss = total_loss / weeks
            bmr = (10 * c_w) + (6.25 * 175) - (5 * 35) + 5
            tdee = int(bmr * 1.375)
            daily_target = int(tdee - (weekly_loss * 7700 / 7)) 
            
            st.subheader("🍽️ 專屬熱量與三大營養素規劃")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("建議每日攝取", f"{daily_target} kcal", f"赤字 {int(tdee - daily_target)} kcal", delta_color="inverse")
            m_col2.metric("🍗 蛋白質", f"{int(c_w * 2)} g")
            m_col3.metric("🍚 碳水化合物", f"{int((daily_target * 0.4) / 4)} g")
            m_col4.metric("🥑 脂肪", f"{int((daily_target * 0.25) / 9)} g")
        else:
            st.warning("喵！目標體重必須比目前體重輕喔！")
    else:
        st.info("👋 喵！請先在上方輸入數值，解鎖專屬計畫。")

# --- Tab 2 ---
with tab2:
    st.subheader("📸 AI 飲食掃描器")
    st.text_input("📝 手動輸入 (例如：排骨便當半碗飯)")
    if st.file_uploader("或上傳餐點照片", type=['jpg', 'png']):
        st.info("🔍 AI 分析結果：預估熱量 680 kcal (蛋白質 35g | 碳水 60g | 脂肪 30g)")

# --- Tab 3 ---
with tab3:
    if c_w > 0:
        st.subheader("🏃‍♂️ 專屬安全運動處方")
        st.markdown('''
        * **🔴 核心肌力 (每週 2 次)：** 深蹲、硬舉等大重量訓練，減脂期維持肌肉量的關鍵。
        * **🎾 靈活心肺 (每週 1-2 次)：** 網球實戰或對打練習，提升心肺耐力。
        * **🚶‍♂️ 基礎活動 (每日)：** 把握通勤空檔，維持每日 8000 步底線。
        > **⚠️ 安全守則：** 不追求極端力竭，關節不適請立刻降階為快走。
        ''')
    else:
        st.info("🔒 請先在第一頁輸入目前體重解鎖喵！")

# --- Tab 4 ---
with tab4:
    if c_w > 0 and t_w > 0:
        st.subheader("📈 每週成效檢討與修正分析")
        weekly_data = pd.DataFrame({
            "週次": ["第 1 週", "第 2 週", "第 3 週", "第 4 週"],
            "理論應減體重 (kg)": [0.45, 0.49, 0.54, 0.51],
            "實際減去體重 (kg)": [0.50, 0.40, 0.10, 0.60] 
        })
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=weekly_data["週次"], y=weekly_data["理論應減體重 (kg)"], name="理論應減", marker_color='#3498db'))
        fig2.add_trace(go.Bar(x=weekly_data["週次"], y=weekly_data["實際減去體重 (kg)"], name="實際掉重", marker_color='#2ecc71'))
        fig2.update_layout(barmode='group')
        st.plotly_chart(fig2, use_container_width=True)
        st.error("🚨 **第 3 週異常分析：** 肌肉水分滯留或隱藏熱量，建議保持原計畫多喝水觀察喵！")
    else:
        st.info("🔒 請先輸入數據解鎖喵！")
