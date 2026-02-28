import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="喵！全能減重戰鬥儀", page_icon="🐾", layout="wide")

# --- 初始化資料庫 ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['日期', '體重', '體脂', '肌肉量', '內臟脂肪', '基礎代謝率', '水分'])
    
# 為了相容新版本，如果舊的 diet_log 沒有日期或餐別，直接重新初始化
if 'diet_log' not in st.session_state or '日期' not in st.session_state.diet_log.columns:
    st.session_state.diet_log = pd.DataFrame(columns=['日期', '餐別', '食物名稱', '熱量(kcal)', '蛋白質(g)', '碳水(g)', '脂肪(g)'])
    
if 'target_w' not in st.session_state: st.session_state.target_w = 0.0
if 'weeks' not in st.session_state: st.session_state.weeks = 12
if 'current_tdee' not in st.session_state: st.session_state.current_tdee = 0
if 'target_p' not in st.session_state: st.session_state.target_p = 0
if 'target_c' not in st.session_state: st.session_state.target_c = 0
if 'target_f' not in st.session_state: st.session_state.target_f = 0
if 'daily_target' not in st.session_state: st.session_state.daily_target = 0

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
        activity_options = {
            "久坐 (幾乎不運動)": 1.2,
            "輕度活動 (1-3天/週)": 1.375,
            "中度活動 (3-5天/週)": 1.55,
            "高度活動 (6-7天/週)": 1.725,
            "極度活動 (高強度)": 1.9
        }
        activity_text = st.selectbox("平常活動狀態", list(activity_options.keys()))

    if st.button("💾 儲存今日數據", use_container_width=True):
        if weight > 0:
            new_data = pd.DataFrame({
                '日期': [pd.to_datetime(record_date).date()],
                '體重': [weight], '體脂': [bf], '肌肉量': [muscle],
                '內臟脂肪': [v_fat], '基礎代謝率': [bmr_input], '水分': [water]
            })
            st.session_state.history = st.session_state.history[st.session_state.history['日期'] != pd.to_datetime(record_date).date()]
            st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
            st.session_state.history = st.session_state.history.sort_values('日期')
            st.success("✅ 儲存成功喵！")
        else:
            st.error("體重必須大於 0 喵！")

    st.divider()

    if weight > 0 and height > 0:
        st.subheader("🎯 Step 2: 你的理想目標")
        t_c1, t_c2 = st.columns(2)
        st.session_state.target_w = t_c1.number_input("目標體重 (kg)", value=st.session_state.target_w, step=0.1)
        st.session_state.weeks = t_c2.slider("預計達成時間 (週)", min_value=4, max_value=52, value=st.session_state.weeks)

        if st.session_state.target_w > 0 and weight > st.session_state.target_w:
            total_loss = weight - st.session_state.target_w
            weekly_loss = total_loss / st.session_state.weeks
            
            calc_bmr = bmr_input if bmr_input > 0 else (10 * weight) + (6.25 * height) - (5 * 35) + 5
            tdee = int(calc_bmr * activity_options[activity_text])
            st.session_state.current_tdee = tdee 
            
            daily_target = int(tdee - (weekly_loss * 7700 / 7)) 
            st.session_state.daily_target = daily_target
            
            # 將三大營養素存入 session_state 供 Tab 2 對比使用
            st.session_state.target_p = int(weight * 2)
            st.session_state.target_c = int((daily_target * 0.4) / 4)
            st.session_state.target_f = int((daily_target * 0.25) / 9)
            
            st.write(f"### 🍽️ 為了在 **{st.session_state.weeks} 週** 內減去 **{total_loss:.1f} kg**：")
            st.write(f"系統判定你的 TDEE 約為 **{tdee} kcal**喵！")
            
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("建議每日攝取", f"{daily_target} kcal", f"赤字 {int(tdee - daily_target)} kcal", delta_color="inverse")
            m_col2.metric("🍗 蛋白質", f"{st.session_state.target_p} g")
            m_col3.metric("🍚 碳水", f"{st.session_state.target_c} g")
            m_col4.metric("🥑 脂肪", f"{st.session_state.target_f} g")

# ==========================================
# Tab 2: 飲食記帳本 (日期、分組、刪除與匯出)
# ==========================================
with tab2:
    st.subheader("🍽️ 新增飲食紀錄")
    
    with st.form("diet_form", clear_on_submit=True):
        col_top1, col_top2 = st.columns(2)
        log_date = col_top1.date_input("飲食日期", datetime.today())
        meal_type = col_top2.selectbox("餐別", ["早餐", "午餐", "晚餐", "點心/宵夜"])
        
        f_name = st.text_input("食物名稱 (如: 雞胸肉)")
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        f_cal = col_f1.number_input("總熱量 (kcal) [可留白]", value=None, min_value=0.0, step=10.0)
        f_p = col_f2.number_input("蛋白質 (g) [可留白]", value=None, min_value=0.0, step=1.0)
        f_c = col_f3.number_input("碳水 (g) [可留白]", value=None, min_value=0.0, step=1.0)
        f_f = col_f4.number_input("脂肪 (g) [可留白]", value=None, min_value=0.0, step=1.0)
        
        submitted = st.form_submit_button("➕ 計算缺項並新增記錄")
        
        if submitted:
            if f_name:
                cal, p, c, f = f_cal, f_p, f_c, f_f
                if cal is None and None not in (p, c, f): cal = (p * 4) + (c * 4) + (f * 9)
                elif cal is not None:
                    if p is None and None not in (c, f): p = max(0.0, (cal - c * 4 - f * 9) / 4)
                    elif c is None and None not in (p, f): c = max(0.0, (cal - p * 4 - f * 9) / 4)
                    elif f is None and None not in (p, c): f = max(0.0, (cal - p * 4 - c * 4) / 9)

                cal = cal if cal is not None else 0.0
                p = p if p is not None else 0.0
                c = c if c is not None else 0.0
                f = f if f is not None else 0.0

                new_food = pd.DataFrame({
                    '日期': [log_date], '餐別': [meal_type], '食物名稱': [f_name], 
                    '熱量(kcal)': [round(cal, 1)], '蛋白質(g)': [round(p, 1)], 
                    '碳水(g)': [round(c, 1)], '脂肪(g)': [round(f, 1)]
                })
                st.session_state.diet_log = pd.concat([st.session_state.diet_log, new_food], ignore_index=True)
                st.success(f"✅ 已將 {f_name} 加入 {log_date} 的 {meal_type} 喵！")
            else:
                st.warning("請先輸入食物名稱喔喵！")

    st.divider()

    # --- 顯示該日紀錄、總計與刪除功能 ---
    view_date = st.date_input("📅 選擇要查看的日期紀錄", datetime.today(), key="view_date")
    daily_df = st.session_state.diet_log[st.session_state.diet_log['日期'] == view_date]
    
    if not daily_df.empty:
        # 計算加總
        total_cal = daily_df['熱量(kcal)'].sum()
        total_p = daily_df['蛋白質(g)'].sum()
        total_c = daily_df['碳水(g)'].sum()
        total_f = daily_df['脂肪(g)'].sum()
        
        t_cal = st.session_state.daily_target
        t_p = st.session_state.target_p
        t_c = st.session_state.target_c
        t_f = st.session_state.target_f

        # 顯示儀表板
        st.subheader(f"📊 {view_date} 的攝取狀況")
        if t_cal > 0:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("總熱量 (kcal)", f"{round(total_cal)} / {t_cal}", f"剩餘 {t_cal - round(total_cal)} kcal", delta_color="normal")
            m2.metric("蛋白質 (g)", f"{round(total_p)} / {t_p}", f"剩餘 {t_p - round(total_p)} g", delta_color="normal")
            m3.metric("碳水 (g)", f"{round(total_c)} / {t_c}", f"剩餘 {t_c - round(total_c)} g", delta_color="normal")
            m4.metric("脂肪 (g)", f"{round(total_f)} / {t_f}", f"剩餘 {t_f - round(total_f)} g", delta_color="normal")

            # 貓咪教練的智能提醒
            st.markdown("### 💡 貓咪教練的加餐建議")
            diff_p = t_p - total_p
            diff_c = t_c - total_c
            diff_f = t_f - total_f
            
            if total_cal > t_cal:
                st.error("⚠️ 逼逼！熱量已經超標囉！接下來請多喝水，或是稍微去散散步消耗一下喵！")
            else:
                if diff_p > 15: st.warning(f"🍗 **蛋白質嚴重不足** (差 {round(diff_p)}g)！下餐建議補充：雞胸肉、雞蛋、無糖豆漿或希臘優格。")
                if diff_c > 20: st.info(f"🍠 **碳水還未達標** (差 {round(diff_c)}g)！可以補充一些優質澱粉：地瓜、燕麥、糙米飯。")
                if diff_f > 10: st.info(f"🥑 **脂肪還可以吃點** (差 {round(diff_f)}g)！建議補充健康油脂：無調味堅果、酪梨、或是一小塊鮭魚。")
                if diff_p <= 15 and diff_c <= 20 and diff_f <= 10:
                    st.success("🎉 太完美了！今天的營養素都快達標且非常均衡，給你一個大大的貓掌印 🐾！")

        # 顯示分餐紀錄與刪除按鈕
        st.markdown("### 📝 詳細明細")
        for meal in ["早餐", "午餐", "晚餐", "點心/宵夜"]:
            meal_df = daily_df[daily_df['餐別'] == meal]
            if not meal_df.empty:
                st.markdown(f"**{meal}**")
                for idx, row in meal_df.iterrows():
                    c_text, c_btn = st.columns([8, 2])
                    c_text.write(f"🍽️ {row['食物名稱']} ➔ **{row['熱量(kcal)']}** kcal (P:{row['蛋白質(g)']} / C:{row['碳水(g)']} / F:{row['脂肪(g)']})")
                    if c_btn.button("❌ 刪除", key=f"del_{idx}"):
                        st.session_state.diet_log = st.session_state.diet_log.drop(idx)
                        st.rerun()

    else:
        st.info(f"{view_date} 暫無飲食紀錄喔喵！")

    st.divider()

    # --- Excel 匯出功能 ---
    st.subheader("📥 匯出飲食紀錄")
    export_days = st.slider("選擇要匯出過去幾天的紀錄 (Excel格式)", 1, 30, 7)
    
    end_date_export = datetime.today().date()
    start_date_export = end_date_export - timedelta(days=export_days)
    
    export_df = st.session_state.diet_log[
        (pd.to_datetime(st.session_state.diet_log['日期']).dt.date >= start_date_export) &
        (pd.to_datetime(st.session_state.diet_log['日期']).dt.date <= end_date_export)
    ]
    
    if not export_df.empty:
        # 使用 BytesIO 將 dataframe 轉換為 Excel 格式 (利用 pandas 內建的 xlsxwriter 或 openpyxl)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, index=False, sheet_name='飲食明細')
        excel_data = output.getvalue()

        st.download_button(
            label=f"📊 下載這 {export_days} 天的紀錄 (Excel)",
            data=excel_data,
            file_name=f"喵教練_飲食紀錄_{end_date_export}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.write("這段期間沒有可以匯出的紀錄喵！")

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
# Tab 4: 目標走勢對決 (歷史 vs 理論 vs 模擬)
# ==========================================
with tab4:
    st.subheader("📈 體重走勢大對決")
    
    df = st.session_state.history.copy()
    if not df.empty and st.session_state.target_w > 0:
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期')
        
        start_date = df['日期'].iloc[0]
        start_weight = df['體重'].iloc[0]
        latest_date = df['日期'].iloc[-1]
        latest_weight = df['體重'].iloc[-1]
        
        end_date = start_date + timedelta(weeks=st.session_state.weeks)
        target_weight = st.session_state.target_w
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x=[start_date, end_date], y=[start_weight, target_weight], mode='lines', 
            name='🎯 理論目標走勢', line=dict(color='rgba(150, 150, 150, 0.7)', width=3, dash='dash')))
        
        fig.add_trace(go.Scatter(x=df['日期'], y=df['體重'], mode='lines+markers', 
            name='📈 過去實際體重', line=dict(color='#ff9f43', width=4), marker=dict(size=8, color='#ff9f43')))
        
        # 使用今天（或最新一筆）的熱量來模擬
        today_df = st.session_state.diet_log[pd.to_datetime(st.session_state.diet_log['日期']).dt.date == datetime.today().date()]
        total_cal_today = today_df['熱量(kcal)'].sum() if not today_df.empty else 0
        current_tdee = st.session_state.current_tdee
        
        if current_tdee > 0 and total_cal_today > 0:
            sim_days = 30
            sim_dates = [latest_date + timedelta(days=i) for i in range(sim_days)]
            actual_deficit = current_tdee - total_cal_today
            loss_per_day = actual_deficit / 7700
            sim_weights = [latest_weight - (loss_per_day * i) for i in range(sim_days)]
            
            fig.add_trace(go.Scatter(x=sim_dates, y=sim_weights, mode='lines', 
                name=f'🚀 未來模擬 (依今日赤字 {int(actual_deficit)}kcal)', line=dict(color='#ff4757', width=3, dash='dot')))
        
        fig.update_layout(title="實際體重 vs 模擬目標走勢", xaxis_title="日期", yaxis_title="體重 (kg)", hovermode="x unified", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **走勢圖怎麼看？** 橘線是過去的紀錄。如果紅色的「未來模擬線」比灰色的「理論目標線」更陡、更低，代表只要維持今天的熱量赤字，你就能提早達標喵！")
    else:
        st.warning("📭 請先在第一頁「儲存數據」並設定「目標」，然後在第二頁「輸入今日飲食」後，就能看到完整的未來模擬圖表喵！")
