import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import datetime

class FitnessTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("飲食與體重趨勢紀錄")
        self.root.geometry("800x800")
        self.root.configure(padx=20, pady=20)

        # === 1. TDEE 計算區塊 ===
        frame_tdee = ttk.LabelFrame(self.root, text="1. 計算 TDEE (每日總熱量消耗)", padding=(10, 10))
        frame_tdee.pack(fill="x", pady=5)

        ttk.Label(frame_tdee, text="基礎代謝率 (BMR):").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_bmr = ttk.Entry(frame_tdee, width=15)
        self.entry_bmr.grid(row=0, column=1, padx=10, pady=5)
        self.entry_bmr.bind("<KeyRelease>", self.calculate_tdee)

        ttk.Label(frame_tdee, text="平常活動狀態:").grid(row=1, column=0, sticky="w", pady=5)
        self.activity_var = tk.DoubleVar(value=1.2)
        activity_options = [
            ("久坐 (幾乎不運動)", 1.2),
            ("輕度活動 (每週運動 1-3 天)", 1.375),
            ("中度活動 (每週運動 3-5 天)", 1.55),
            ("高度活動 (每週運動 6-7 天)", 1.725),
            ("極度活動 (勞力工作或高強度訓練)", 1.9)
        ]
        self.combo_activity = ttk.Combobox(frame_tdee, width=30, state="readonly")
        self.combo_activity['values'] = [text for text, val in activity_options]
        self.combo_activity.current(0)
        self.combo_activity.grid(row=1, column=1, padx=10, pady=5)
        self.combo_activity.bind("<<ComboboxSelected>>", self.update_activity_val)

        self.label_tdee_result = ttk.Label(frame_tdee, text="目前 TDEE: 0 大卡", foreground="red", font=("Arial", 11, "bold"))
        self.label_tdee_result.grid(row=2, column=0, columnspan=2, sticky="w", pady=10)

        self.activity_dict = {text: val for text, val in activity_options}

        # === 2. 食物熱量與營養素輸入區塊 ===
        frame_food = ttk.LabelFrame(self.root, text="2. 食物熱量與營養素 (輸入部分數值後點擊自動補全)", padding=(10, 10))
        frame_food.pack(fill="x", pady=5)

        labels = ["總熱量 (kcal)", "蛋白質 (g)", "碳水化合物 (g)", "脂肪 (g)"]
        self.entries_macro = {}
        for i, text in enumerate(labels):
            ttk.Label(frame_food, text=text).grid(row=0, column=i, padx=5, pady=5)
            entry = ttk.Entry(frame_food, width=12)
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.entries_macro[text] = entry

        btn_auto_fill = ttk.Button(frame_food, text="自動計算缺項", command=self.auto_fill_macros)
        btn_auto_fill.grid(row=2, column=0, columnspan=4, pady=10)

        frame_settings = ttk.Frame(frame_food)
        frame_settings.grid(row=3, column=0, columnspan=4, pady=5, sticky="w")
        ttk.Label(frame_settings, text="目前體重 (kg):").pack(side="left")
        self.entry_weight = ttk.Entry(frame_settings, width=10)
        self.entry_weight.insert(0, "70")
        self.entry_weight.pack(side="left", padx=5)

        # === 3. 趨勢圖區塊 ===
        frame_chart = ttk.LabelFrame(self.root, text="3. 體重趨勢圖 (未來 30 天模擬)", padding=(10, 10))
        frame_chart.pack(fill="both", expand=True, pady=5)

        btn_update_chart = ttk.Button(frame_chart, text="更新赤字與圖表", command=self.update_chart)
        btn_update_chart.pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(7, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_chart)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.current_tdee = 0

    def update_activity_val(self, event=None):
        selected_text = self.combo_activity.get()
        self.activity_var.set(self.activity_dict[selected_text])
        self.calculate_tdee()

    def calculate_tdee(self, event=None):
        try:
            bmr = float(self.entry_bmr.get())
            activity = self.activity_var.get()
            self.current_tdee = bmr * activity
            self.label_tdee_result.config(text=f"目前 TDEE: {round(self.current_tdee)} 大卡")
        except ValueError:
            self.current_tdee = 0
            self.label_tdee_result.config(text="目前 TDEE: 0 大卡")

    def get_float_or_none(self, entry):
        val = entry.get().strip()
        if not val:
            return None
        try:
            return float(val)
        except ValueError:
            return None

    def auto_fill_macros(self):
        cal = self.get_float_or_none(self.entries_macro["總熱量 (kcal)"])
        p = self.get_float_or_none(self.entries_macro["蛋白質 (g)"])
        c = self.get_float_or_none(self.entries_macro["碳水化合物 (g)"])
        f = self.get_float_or_none(self.entries_macro["脂肪 (g)"])

        # 情況 A: 有三大營養素，算總熱量
        if cal is None and None not in (p, c, f):
            cal = p * 4 + c * 4 + f * 9
            self.entries_macro["總熱量 (kcal)"].delete(0, tk.END)
            self.entries_macro["總熱量 (kcal)"].insert(0, str(round(cal, 1)))
        
        # 情況 B: 有總熱量及其中兩個，算剩下的一個
        elif cal is not None:
            if p is None and None not in (c, f):
                p = (cal - c * 4 - f * 9) / 4
                self.entries_macro["蛋白質 (g)"].delete(0, tk.END)
                self.entries_macro["蛋白質 (g)"].insert(0, str(max(0, round(p, 1))))
            elif c is None and None not in (p, f):
                c = (cal - p * 4 - f * 9) / 4
                self.entries_macro["碳水化合物 (g)"].delete(0, tk.END)
                self.entries_macro["碳水化合物 (g)"].insert(0, str(max(0, round(c, 1))))
            elif f is None and None not in (p, c):
                f = (cal - p * 4 - c * 4) / 9
                self.entries_macro["脂肪 (g)"].delete(0, tk.END)
                self.entries_macro["脂肪 (g)"].insert(0, str(max(0, round(f, 1))))

    def update_chart(self):
        try:
            weight = float(self.entry_weight.get())
            intake_cal = float(self.entries_macro["總熱量 (kcal)"].get())
        except ValueError:
            messagebox.showwarning("輸入錯誤", "請確保體重與總熱量皆已填寫完整數值。")
            return

        if self.current_tdee <= 0:
            messagebox.showwarning("輸入錯誤", "請先輸入正確的 BMR 並選擇活動量以計算 TDEE。")
            return

        self.ax.clear()

        # 準備資料：未來 30 天
        days = 30
        today = datetime.date.today()
        dates = [today + datetime.timedelta(days=i) for i in range(days)]
        
        # 理論赤字：假設標準每天 -500 大卡 (約每週減 0.5kg)
        theoretical_deficit = 500
        theoretical_loss_per_day = theoretical_deficit / 7700
        theoretical_weights = [weight - (theoretical_loss_per_day * i) for i in range(days)]

        # 實際模擬赤字：依照目前 TDEE 減去輸入的總攝取熱量
        actual_deficit = self.current_tdee - intake_cal
        actual_loss_per_day = actual_deficit / 7700
        actual_weights = [weight - (actual_loss_per_day * i) for i in range(days)]

        # 繪圖
        self.ax.plot(dates, theoretical_weights, linestyle='--', color='blue', label='理論目標 (每日 -500kcal)')
        self.ax.plot(dates, actual_weights, linestyle='-', color='red', label=f'實際模擬 (目前赤字 {round(actual_deficit)}kcal)')

        # 設定 X 軸為日期格式
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        self.fig.autofmt_xdate()

        self.ax.set_title("未來 30 天體重下降模擬")
        self.ax.set_ylabel("體重 (kg)")
        self.ax.legend()
        self.ax.grid(True, linestyle=':', alpha=0.6)

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessTrackerApp(root)
    root.mainloop()
