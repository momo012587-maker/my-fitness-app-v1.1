import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="喵！全能減重戰鬥儀", page_icon="🐾", layout="wide")

# --- 初始化資料庫 ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['日期', '體重', '體脂', '肌肉量', '內臟脂肪', '基礎代謝率', '水分'])
if 'diet_log' not in st.session_state:
    st.session_state.diet_log = pd.DataFrame(columns=['食物名稱', '熱量(kcal)', '蛋白質(g)', '碳水(g)', '脂肪(g)'])
if 'target_w' not in st.session_state:
    st.session_state.target_w = 0.0
if 'weeks' not in st.session_state:
    st.session_state.weeks = 12

st.title("🐾 喵！全能減重戰鬥星艦")
st.write("精準診斷、自動算熱量，並用走勢圖對決你的目標喵！")

tab1, tab2, tab3, tab4 = st.tabs(["📊 1. 數據與診斷", "🍽️ 2. 飲食記帳", "🏃‍♂️ 3. 運動處方", "📈 4. 目標走勢對決"])

# ==========================================
# Tab 1: 身體數據與優劣勢診斷
# ==========================================
with tab1:
    st.subheader("📑 Step 1: 記錄今日身體數據")
    record_date = st.date_input("選擇紀錄日期", datetime.today())
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        height = st.number_input("身高 (cm)", value=0.0, step=0.1)
        weight = st.number_input("體重 (kg)", value=0.0, step=0.1)
    with col2:
        bf = st.number_input("體脂肪率 (%)", value=0.0, step=0.1)
        muscle = st.number_input("肌肉量 (kg)", value=0.0, step=0.1)
    with col3:
        v_fat = st.number_input("內臟脂肪指數", value=0.0, step=0.5)
        bmr_input = st.number_input("基礎代謝 (kcal)", value=0, step=10)
    with col4:
        water = st.number_input("身體水分 (kg)", value=0.0, step=0.1)
        st.write(" ")
        if st.button("💾 儲存今日數據", use_container_width=True):
            if weight > 0:
                new_data = pd.DataFrame({
                    '日期': [pd.to_datetime(record_date)],
                    '體重': [weight], '體脂': [bf], '肌肉量': [muscle],
                    '內臟脂肪': [v_fat], '基礎代謝率': [bmr_input], '水分': [water]
                })
                st.session_state.history = st.session_state.history[st.session_state.history['日期'] != pd.to_datetime(record_date)]
                st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
                st.session_state.history = st.session_state.history.sort_values('日期')
                st.success(f"✅ 儲存成功！")
            else:
                st.error("體重必須大於 0 喵！")

    st.divider()

    # --- 新增：優勢與劣勢分析 ---
    if weight > 0 and height > 0:
        st.subheader("🩺 貓咪教練的身體組成分析")
        bmi = weight / ((height/100)**2)
        
        strengths = []
        weaknesses = []
        
        # 分析邏輯
        if bmi > 24:
            if muscle > (weight * 0.4): 
                strengths.append(f"BMI ({bmi:.1f}) 雖然偏高，但既然有保持重訓習慣，這通常是因為高肌肉量造成的，不需對 BMI 過度恐慌，我們專注看體脂率就好。")
            else:
                weaknesses.append(f"BMI ({bmi:.1f}) 落在過重區間，需要開始控制熱量囉。")
        else:
            strengths.append(f"BMI ({bmi:.1f}) 落在健康標準範圍內！")

        if bf > 0:
            if bf < 15: strengths.append(f"體脂率 ({bf}%) 非常精實，腹肌線條應該很明顯了！")
            elif 15 <= bf <= 20: strengths.append(f"體脂率 ({bf}%) 落在一般男性的健康標準內，維持得不錯。")
            else: weaknesses.append(f"體脂率 ({bf}%) 偏高，這將是我們接下來減脂的首要打擊目標。")
            
        if v_fat > 0:
            if v_fat < 10: strengths.append(f"內臟脂肪 ({v_fat}) 安全！代表內臟負擔小，飲食狀態算乾淨。")
            else: weaknesses.append(f"內臟脂肪 ({v_fat}) 偏高，可能有脂肪肝或心血管隱憂，強烈建議減少精緻糖與酒精。")

        c1, c2 = st.columns(2)
        with c1:
            st.info("**✅ 你的優勢**\n\n" + "\n\n".join([f"- {s}" for s in strengths]) if strengths else "輸入更多數據以獲取優勢分析！")
        with c2:
            st.warning("**⚠️ 需注意的劣勢**\n\n" + "\n\n".join([f"- {w}" for w in weaknesses]) if weaknesses else "目前數據看起來很健康，繼續保持！")

    st.divider()

    # --- 目標設定 ---
    st.subheader("🎯 Step 2: 你的理想目標")
    t_c1, t_c2 = st.columns(2)
    st.session_state.target_w = t_c1.number_input("目標體重 (kg)", value=st.session_state.target_w, step=0.1)
    st.session_state.weeks = t_c2.slider("預計達成時間 (週)", min_value=4, max_value=52, value=st.session_state.weeks)

    if weight > 0 and st.session_state.target_w > 0:
        if weight > st.session_state.target_w:
            total_loss = weight - st.session_state.target_w
            weekly_loss = total_loss / st.session_state.weeks
            calc_bmr = bmr_input if bmr_input > 0 else (10 * weight) + (6.25 * height) - (5 * 35) + 5
            tdee = int(calc_bmr * 1.375)
            daily_target = int(tdee - (weekly_loss * 7700 / 7)) 
            st.session_state.daily_target = daily_target
            
            st.write(f"### 🍽️ 為了在 **{st.session_state.weeks} 週** 內減去 **{total_loss:.1f} kg**：")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("建議每日攝取", f"{daily_target} kcal", f"赤字 {int(tdee - daily_target)} kcal", delta_color="inverse")
            m_col2.metric("🍗 蛋白質", f"{int(weight * 2)} g")
            m_col3.metric("🍚 碳水", f"{int((daily_target * 0.4) / 4)} g")
            m_col4.metric("🥑 脂肪", f"{int((daily_target * 0.25) / 9)} g")

# ==========================================
# Tab 2: 飲食記帳本 (自動計算熱量)
# ==========================================
with tab2:
    st.subheader("🍽️ 營養素記帳本 (程式自動算熱量)")
    
    with st.form("diet_form", clear_on_submit=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        f_name = col_f1.text_input("食物名稱 (如: 雞胸肉)")
        f_p = col_f2.number_input("蛋白質 (g)", min_value=0, step=1)
        f_c = col_f3.number_input("碳水化合物 (g)", min_value=0, step=1)
        f_f = col_f4.number_input("脂肪 (g)", min_value=0, step=1)
        
        if st.form_submit_button("➕ 計算熱量並新增"):
            if f_name:
                calc_cal = (f_p * 4) + (f_c * 4) + (f_f * 9) # 程式自動計算
                new_food = pd.DataFrame({'食物名稱': [f_name], '熱量(kcal)': [calc_cal], '蛋白質(g)': [f_p], '碳水(g)': [f_c], '脂肪(g)': [f_f]})
                st.session_state.diet_log = pd.concat([st.session_state.diet_log, new_food], ignore_index=True)
                st.success(f"✅ {f_name} 已新增！自動計算熱量為 {calc_cal} kcal。")

    if not st.session_state.diet_log.empty:
        st.dataframe(st.session_state.diet_log, use_container_width=True)
        total_cal = st.session_state.diet_log['熱量(kcal)'].sum()
        target = st.session_state.get('daily_target', 0)
        
        if target > 0:
            st.metric("今日已攝取 / 建議總量", f"{total_cal} / {target} kcal", f"剩餘扣打 {target - total_cal} kcal", delta_color="normal")
        if st.button("🗑️ 清空今日清單"):
            st.session_state.diet_log = st.session_state.diet_log.iloc[0:0]
            st.rerun()

# ==========================================
# Tab 3: 運動處方
# ==========================================
with tab3:
    st.subheader("🏃‍♂️ 專屬安全運動處方")
    st.write("目前依據你的身體指標，建議如下：")
    st.markdown('''
    * **🔴 阻力訓練：** 優先強化核心與下肢，多做深蹲、硬舉等大肌群動作，有助於維持代謝。
    * **🎾 靈活心肺：** 將有氧融入興趣中（如網球），比單純跑步更能持之以恆。
    * **🚶‍♂️ 日常 NEAT：** 跑業務時盡量用走路取代短程騎車，增加非運動性熱量消耗。
    ''')

# ==========================================
# Tab 4: 目標走勢對決 (實際 vs 理論模擬)
# ==========================================
with tab4:
    st.subheader("📈 體重走勢大對決")
    
    df = st.session_state.history.copy()
    if not df.empty and st.session_state.target_w > 0:
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期')
        
        # 抓取第一筆資料作為起點
        start_date = df['日期'].iloc[0]
        start_weight = df['體重'].iloc[0]
        
        # 計算理論終點
        end_date = start_date + timedelta(weeks=st.session_state.weeks)
        target_weight = st.session_state.target_w
        
        fig = go.Figure()
        
        # 1. 畫出理論目標走勢 (灰色虛線)
        fig.add_trace(go.Scatter(
            x=[start_date, end_date], 
            y=[start_weight, target_weight], 
            mode='lines', 
            name='🎯 理論目標走勢 (基於你的赤字設定)', 
            line=dict(color='rgba(150, 150, 150, 0.7)', width=3, dash='dash')
        ))
        
        # 2. 畫出實際體重走勢 (橘色實線)
        fig.add_trace(go.Scatter(
            x=df['日期'], 
            y=df['體重'], 
            mode='lines+markers', 
            name='📈 你的實際體重', 
            line=dict(color='#ff9f43', width=4),
            marker=dict(size=8, color='#ff9f43')
        ))
        
        fig.update_layout(
            title="實際體重 vs 模擬目標走勢",
            xaxis_title="日期",
            yaxis_title="體重 (kg)",
            hovermode="x unified",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **走勢圖怎麼看？** 如果橘線（實際體重）落在灰線（目標走勢）的下方，代表你減重進度超前！如果跑到灰線上方，代表你需要稍微嚴格控制飲食或增加活動量了喵！")
        
        st.write("### 🗃️ 歷史紀錄明細")
        st.dataframe(df.sort_values('日期', ascending=False), use_container_width=True)
    else:
        st.warning("📭 請先在第一頁「儲存至少一筆身體數據」並設定「目標體重」，才能產生走勢對決圖喵！")
