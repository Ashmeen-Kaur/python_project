import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------- Sample Air Quality Data ----------
df = pd.DataFrame({
    'Date': pd.date_range('2025-07-01', periods=10),
    'PM2.5': [45, 85, 120, 160, 200, 250, 55, 40, 180, 95],
    'PM10':  [100, 150, 220, 180, 210, 300, 120, 90, 250, 160],
    'NO2':   [60, 70, 75, 85, 90, 95, 50, 40, 82, 78]
})

thresholds = {'PM2.5': 100, 'PM10': 200, 'NO2': 80}
aqi_map = {
    1: "Good", 2: "Moderate", 3: "Unhealthy for Sensitive Groups",
    4: "Unhealthy", 5: "Very Unhealthy", 6: "Hazardous"
}
tips = {
    1: "Enjoy outdoor activities!",
    2: "Air is fine, be mindful if sensitive.",
    3: "Sensitive groups should limit activity.",
    4: "Avoid strenuous outdoor work.",
    5: "Stay indoors if possible.",
    6: "Use air purifiers, avoid going out!"
}

def get_aqi(pm): return next((i for i, v in enumerate([50, 100, 150, 200, 300], 1) if pm <= v), 6)
def alerts(row): return ", ".join(f"{p} High" for p in thresholds if row[p] > thresholds[p]) or "Safe"

df['Alert'] = df.apply(alerts, axis=1)
df['AQI'] = df['PM2.5'].apply(get_aqi)
df['Category'] = df['AQI'].map(aqi_map)

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("🌍 AirAware Alert")
root.geometry("800x600")
root.configure(bg="#f1f7fb")

style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 11), padding=6)
style.configure("TLabel", background="#f1f7fb", font=("Segoe UI", 12))

user_name = tk.StringVar()

def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()

# ---------- Home ----------
def home_screen():
    clear_frame()
    tk.Label(root, text="🌤️ AirAware Alert", font=("Segoe UI", 22, "bold"), bg="#f1f7fb", fg="#2c3e50").pack(pady=20)
    tk.Label(root, text="Enter your name:", font=("Segoe UI", 14), bg="#f1f7fb").pack()
    tk.Entry(root, textvariable=user_name, font=("Segoe UI", 13), width=25).pack(pady=10)

    btn_frame = tk.Frame(root, bg="#f1f7fb")
    btn_frame.pack(pady=20)

    options = [
        ("View Air Quality Table", view_table),
        ("AQI Summary", aqi_summary),
        ("Health Tip", health_tip),
        ("Plot Trends", plot_trends),
        ("Search by Date", search_by_date),
        ("Exit", root.quit)
    ]

    for text, command in options:
        ttk.Button(btn_frame, text=text, command=command).pack(pady=5, ipadx=5, fill='x', padx=50)

# ---------- View Table ----------
def view_table():
    clear_frame()
    tk.Label(root, text="📋 Air Quality Data", font=("Segoe UI", 18, "bold"), bg="#f1f7fb").pack(pady=10)

    tree = ttk.Treeview(root, columns=df.columns.tolist(), show='headings')
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')
    for _, row in df.iterrows():
        tree.insert('', tk.END, values=list(row))
    tree.pack(pady=10, expand=True, fill="both")

    ttk.Button(root, text="⬅ Back", command=home_screen).pack(pady=10)

# ---------- AQI Summary ----------
def aqi_summary():
    clear_frame()
    tk.Label(root, text="📊 AQI Category Summary", font=("Segoe UI", 18, "bold"), bg="#f1f7fb").pack(pady=20)
    summary = df['Category'].value_counts()
    for cat, count in summary.items():
        ttk.Label(root, text=f"{cat}: {count} day(s)").pack()

    ttk.Button(root, text="⬅ Back", command=home_screen).pack(pady=20)

# ---------- Health Tip ----------
def health_tip():
    clear_frame()
    tk.Label(root, text="💡 Health Tip by Date", font=("Segoe UI", 18, "bold"), bg="#f1f7fb").pack(pady=20)

    dates = df['Date'].dt.date.astype(str).tolist()
    selected_date = tk.StringVar(value=dates[-1])

    ttk.Label(root, text="Select a date:").pack(pady=5)
    dropdown = ttk.Combobox(root, textvariable=selected_date, values=dates, state="readonly", font=("Segoe UI", 12))
    dropdown.pack(pady=5)

    tip_frame = tk.Frame(root, bg="#ffffff")
    tip_frame.pack(pady=20, padx=30, fill="both", expand=True)

    def show_tip():
        for widget in tip_frame.winfo_children():
            widget.destroy()
        try:
            date = pd.to_datetime(selected_date.get()).date()
            row = df[df['Date'].dt.date == date].iloc[0]
            aqi_level = row['AQI']
            category = row['Category']
            tip = tips[aqi_level]

            emoji_map = {
                1: "😊", 2: "😐", 3: "😷",
                4: "🤒", 5: "🤢", 6: "☠️"
            }
            color_map = {
                1: "#d4edda", 2: "#fff3cd", 3: "#ffeeba",
                4: "#f8d7da", 5: "#f5c6cb", 6: "#e2e3e5"
            }

            bg_color = color_map[aqi_level]
            emoji = emoji_map[aqi_level]

            tip_frame.configure(bg=bg_color)

            tk.Label(tip_frame, text=f"{emoji} Air Quality on {date}: {category}", font=("Segoe UI", 20, "bold"),
                     bg=bg_color).pack(pady=10)
            tk.Label(tip_frame, text=f"PM2.5: {row['PM2.5']} | PM10: {row['PM10']} | NO₂: {row['NO2']}",
                     font=("Segoe UI", 13), bg=bg_color).pack(pady=5)
            tk.Label(tip_frame, text=f"💡 Tip: {tip}", font=("Segoe UI", 14), wraplength=600, justify="center",
                     bg=bg_color).pack(pady=15)

            if aqi_level >= 4:
                tk.Label(tip_frame, text="⚠️ Use a mask and keep windows shut!", font=("Segoe UI", 11, "italic"),
                         bg=bg_color, fg="darkred").pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(root, text="Show Tip", command=show_tip).pack(pady=10)
    ttk.Button(root, text="⬅ Back", command=home_screen).pack(pady=10)

# ---------- Plot Trends ----------
def plot_trends():
    clear_frame()
    tk.Label(root, text="📈 Air Quality Trends", font=("Segoe UI", 18, "bold"), bg="#f1f7fb").pack(pady=10)

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.set(style="whitegrid")

    for pollutant, marker in zip(['PM2.5', 'PM10', 'NO2'], ['o', 's', '^']):
        ax.plot(df['Date'], df[pollutant], label=pollutant, marker=marker)
        ax.axhline(y=thresholds[pollutant], linestyle='--', label=f"{pollutant} Limit")

    ax.set_title("Air Quality Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Pollutant Level")
    ax.legend()
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill='both')

    ttk.Button(root, text="⬅ Back", command=home_screen).pack(pady=10)

# ---------- Search by Date ----------
def search_by_date():
    clear_frame()
    tk.Label(root, text="🔎 Search by Date", font=("Segoe UI", 18, "bold"), bg="#f1f7fb").pack(pady=20)

    entry = tk.Entry(root, font=("Segoe UI", 12))
    entry.pack(pady=10)
    tk.Label(root, text="(Format: YYYY-MM-DD)", font=("Segoe UI", 10), bg="#f1f7fb").pack()

    def find_date():
        date_str = entry.get().strip()
        try:
            date = pd.to_datetime(date_str).date()
            match = df[df['Date'].dt.date == date]
            if match.empty:
                messagebox.showinfo("No Data", f"No data found for {date}")
            else:
                row = match.iloc[0]
                msg = f"📅 {date}\nAQI: {row['Category']}\nPM2.5: {row['PM2.5']}\nPM10: {row['PM10']}\nNO2: {row['NO2']}\nAlert: {row['Alert']}"
                messagebox.showinfo("Air Quality", msg)
        except:
            messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")

    ttk.Button(root, text="Search", command=find_date).pack(pady=10)
    ttk.Button(root, text="⬅ Back", command=home_screen).pack(pady=10)

if __name__ == "__main__":
    home_screen()
    root.mainloop()
