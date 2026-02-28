import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="喵！全能減重戰鬥儀", page_icon="🐾", layout="wide")

# --- 1. 初始化資料庫 (Session State) ---
# 確保網頁重整時，歷史數據不會消失（除非關閉瀏覽器）
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['日期', '體重', '體脂', '肌肉量', '內臟脂肪', '基礎代謝率', '水分', '腰圍', '臀圍'])

if 'diet_log' not in st.session_state:
    st.session_state.diet_log = pd.DataFrame(columns=['食物名稱', '熱量(kcal)', '蛋白質(g)', '碳水(g)', '脂肪(g)'])

st.title("🐾 喵！全能減重戰鬥星艦 (純淨手動版)")
st.write("沒有假數據，沒有幻覺。你輸入什麼，系統就分析什麼喵！")

tab1, tab2, tab3, tab4 = st.tabs(["📊 1. 身體數據與目標", "🍽️ 2. 飲食記帳本", "🏃‍♂️ 3. 運動處方", "📈 4. 歷史統計圖表"])

# ==========================================
# Tab 1: 身體數據與目標 (全手動輸入)
# ==========================================
with tab1:
    st.subheader("📑 Step 1: 手動輸入今日身體數據")
    
    # 為了方便測試圖表，允許選擇日期
    record_date = st.date_input("選擇紀錄日期", datetime.today())
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        height = st.number_input("身高 (cm)", value=0.0, step=0.1)
        weight = st.number_input("體重 (kg)", value=0.0, step=0.1)
        bf = st.number_input("體脂肪率 (%)", value=0.0, step=0.1)
    with col2:
        muscle = st.number_input("肌肉量 (kg)", value=0.0, step=0.1)
        bmr_input = st.number_input("基礎代謝率 BMR (kcal)", value=0, step=10)
        water = st.number_input("身體水分 (kg)", value=0.0, step=0.1)
    with col3:
        v_fat = st.number_input("內臟脂肪指數", value=0.0, step=0.5)
        waist = st.number_input("腰圍 (cm)", value=0.0, step=0.1)
        hip = st.number_input("臀圍 (cm)", value=0.0, step=0.1)
    with col4:
        # 儲存按鈕
        st.write("確認無誤後請儲存：")
        if st.button("💾 儲存今日身體數據", use_container_width=True):
            if weight > 0:
                new_data = pd.DataFrame({
                    '日期': [pd.to_datetime(record_date)],
                    '體重': [weight], '體脂': [bf], '肌肉量': [muscle],
                    '內臟脂肪': [v_fat], '基礎代謝率': [bmr_input], 
                    '水分': [water], '腰圍': [waist], '臀圍': [hip]
                })
                # 移除同一天的舊紀錄，寫入新紀錄
                st.session_state.history = st.session_state.history[st.session_state.history['日期'] != pd.to_datetime(record_date)]
                st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
                st.session_state.history = st.session_state.history.sort_values('日期')
                st.success(f"✅ {record_date} 數據已成功儲存！請至「歷史統計圖表」查看。")
            else:
                st.error("❌ 體重必須大於 0 才能儲存喵！")

    st.divider()
    
    st.subheader("🎯 Step 2: 你的理想目標")
    col_t1, col_t2, col_t3 = st.columns(3)
    target_weight = col_t1.number_input("目標體重 (kg)", value=0.0, step=0.1)
    target_bf = col_t2.number_input("目標體脂 (%)", value=0.0, step=0.1)
    weeks = col_t3.slider("預計達成時間 (週)", min_value=4, max_value=52, value=12) # 上限 52 週

    # 目標計算邏輯 (只有體重有輸入才顯示)
    if weight > 0 and target_weight > 0 and height > 0:
        if weight > target_weight:
            # 計算 BMI 與腰臀比
            bmi = weight / ((height/100)**2)
            whr = waist / hip if hip > 0 else 0
            
            st.info(f"🩺 **你的目前體態指標**：BMI = {bmi:.1f} | 腰臀比 = {whr:.2f} (大於0.9需注意心血管風險)")
            
            total_loss = weight - target_weight
            weekly_loss = total_loss / weeks
            
            # TDEE 計算 (優先使用手動輸入的 BMR，若為0則用公式)
            calc_bmr = bmr_input if bmr_input > 0 else (10 * weight) + (6.25 * height) - (5 * 35) + 5
            tdee = int(calc_bmr * 1.375) # 預設輕度活動
            daily_target = int(tdee - (weekly_loss * 7700 / 7)) 
            
            # 儲存每日目標熱量供飲食頁面使用
            st.session_state.daily_target = daily_target
            
            st.subheader("🍽️ 系統建議：專屬熱量與三大營養素規劃")
            st.write(f"為了在 **{weeks} 週** 內安全減去 **{total_loss:.1f} kg** (每週約降 {weekly_loss:.2f} kg)：")
            
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("建議每日攝取", f"{daily_target} kcal", f"每日赤字 {int(tdee - daily_target)} kcal", delta_color="inverse")
            m_col2.metric("🍗 蛋白質 (保肌基底)", f"{int(weight * 2)} g")
            m_col3.metric("🍚 碳水化合物", f"{int((daily_target * 0.4) / 4)} g")
            m_col4.metric("🥑 脂肪", f"{int((daily_target * 0.25) / 9)} g")
        else:
            st.warning("喵！目標體重必須比目前體重輕喔！")
    else:
        st.warning("請輸入「身高、目前體重、目標體重」以解鎖熱量規劃。")

# ==========================================
# Tab 2: 飲食記帳本 (全手動算數版)
# ==========================================
with tab2:
    st.subheader("🍽️ 每日飲食手動記帳本")
    st.write("由於未串接 AI 視覺，請在此手動輸入你今天吃的食物與熱量。")
    
    with st.form("diet_form", clear_on_submit=True):
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        f_name = col_f1.text_input("食物名稱")
        f_cal = col_f2.number_input("熱量(kcal)", min_value=0, step=10)
        f_p = col_f3.number_input("蛋白質(g)", min_value=0, step=1)
        f_c = col_f4.number_input("碳水(g)", min_value=0, step=1)
        f_f = col_f5.number_input("脂肪(g)", min_value=0, step=1)
        
        submitted = st.form_submit_button("➕ 新增至今日清單")
        if submitted and f_name:
            new_food = pd.DataFrame({'食物名稱': [f_name], '熱量(kcal)': [f_cal], '蛋白質(g)': [f_p], '碳水(g)': [f_c], '脂肪(g)': [f_f]})
            st.session_state.diet_log = pd.concat([st.session_state.diet_log, new_food], ignore_index=True)
            st.success(f"已新增：{f_name}")

    # 顯示今日飲食結算
    if not st.session_state.diet_log.empty:
        st.dataframe(st.session_state.diet_log, use_container_width=True)
        
        total_cal = st.session_state.diet_log['熱量(kcal)'].sum()
        target = st.session_state.get('daily_target', 0)
        
        st.write("### 📊 今日總結")
        if target > 0:
            st.metric("今日已攝取 / 目標熱量", f"{total_cal} / {target} kcal", f"剩餘 {target - total_cal} kcal", delta_color="normal")
        else:
            st.metric("今日已攝取總熱量", f"{total_cal} kcal")
        
        if st.button("🗑️ 清空今日飲食紀錄"):
            st.session_state.diet_log = st.session_state.diet_log.iloc[0:0]
            st.rerun()

# ==========================================
# Tab 3: 安全運動處方 (無假數據)
# ==========================================
with tab3:
    st.subheader("🏃‍♂️ 專屬安全運動處方")
    if 'history' in st.session_state and not st.session_state.history.empty:
        latest_data = st.session_state.history.iloc[-1]
        w = latest_data['體重']
        m = latest_data['肌肉量']
        
        st.write(f"基於你最新的體重 ({w}kg) 與 肌肉量 ({m}kg)，建議如下：")
        st.markdown('''
        * **🚶‍♂️ 基礎心肺：** 建議以「快走、上坡走」為主，保護膝蓋關節。
        * **🔴 阻力訓練：** 優先強化下肢與核心（深蹲、臀推），提升基礎代謝。
        * **⚠️ 注意事項：** 運動後請隨時補充水分，若有關節不適請立即停止。
        ''')
    else:
        st.info("🔒 請先至第一頁儲存你的身體數據，以解鎖運動處方。")

# ==========================================
# Tab 4: 歷史統計圖表 (完全動態化，有資料才畫圖)
# ==========================================
with tab4:
    st.subheader("📈 真實歷史數據追蹤")
    
    if st.session_state.history.empty:
        st.warning("📭 目前尚無任何歷史紀錄。請回到第一頁，輸入數據並點擊「儲存今日身體數據」後，圖表才會顯示喵！")
    else:
        df = st.session_state.history.copy()
        df['日期'] = pd.to_datetime(df['日期'])
        
        # 讓使用者選擇時間維度
        view_mode = st.radio("選擇統計維度", ["日", "週", "月", "年"], horizontal=True)
        
        # 根據選擇進行資料分組 (Resample)
        if view_mode == "日":
            df_plot = df.groupby(df['日期'].dt.date).mean().reset_index()
        elif view_mode == "週":
            df_plot = df.groupby(df['日期'].dt.to_period('W').apply(lambda r: r.start_time)).mean().reset_index()
            df_plot['日期'] = df_plot['日期'].dt.date
        elif view_mode == "月":
            df_plot = df.groupby(df['日期'].dt.to_period('M').apply(lambda r: r.start_time)).mean().reset_index()
            df_plot['日期'] = df_plot['日期'].dt.strftime('%Y-%m')
        else: # 年
            df_plot = df.groupby(df['日期'].dt.to_period('Y').apply(lambda r: r.start_time)).mean().reset_index()
            df_plot['日期'] = df_plot['日期'].dt.strftime('%Y')

        # 繪製動態折線圖 (體重 vs 體脂)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_plot['日期'], y=df_plot['體重'], mode='lines+markers', name='體重 (kg)', line=dict(color='#ff9f43', width=3)))
        fig.add_trace(go.Scatter(x=df_plot['日期'], y=df_plot['體脂'], mode='lines+markers', name='體脂率 (%)', line=dict(color='#3498db', width=3), yaxis='y2'))
        
        # 設定雙 Y 軸
        fig.update_layout(
            title=f"體重與體脂率趨勢 ({view_mode}報表)",
            xaxis=dict(title="時間"),
            yaxis=dict(title="體重 (kg)", titlefont=dict(color="#ff9f43"), tickfont=dict(color="#ff9f43")),
            yaxis2=dict(title="體脂率 (%)", titlefont=dict(color="#3498db"), tickfont=dict(color="#3498db"), anchor="x", overlaying="y", side="right"),
            hovermode="x unified",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 顯示詳細數據表
        st.write("### 🗃️ 詳細歷史數據表")
        st.dataframe(df.sort_values('日期', ascending=False), use_container_width=True)
        
        # 開發者除錯用：清空資料庫按鈕
        if st.button("🚨 (危險) 清空所有歷史紀錄"):
            st.session_state.history = st.session_state.history.iloc[0:0]
            st.rerun()
