import tkinter as tk
from tkinter import ttk, messagebox
import time
from datetime import datetime
import json
import csv
import threading
import winsound
from collections import deque

# ==================== STYLING CONFIGURATION ====================
# Plant-inspired color palette
COLORS = {
    'primary': '#2E7D32',      # Deep forest green
    'primary_dark': '#1B5E20',  # Darker green for hover/active
    'primary_light': '#4CAF50', # Light green
    'secondary': '#81C784',     # Soft green
    'accent': '#FF9800',        # Warm orange (fruit/soil accent)
    'accent_light': '#FFB74D',  # Light orange
    'background': '#F1F8E9',    # Very light green background
    'surface': '#FFFFFF',       # White surface
    'surface_light': '#F5F5F5', # Light gray surface
    'text': '#1B5E20',          # Dark green text
    'text_secondary': '#558B2F', # Medium green text
    'error': '#D32F2F',         # Red for errors/critical
    'warning': '#FF9800',       # Orange for warnings
    'success': '#4CAF50',       # Green for success
    'info': '#2196F3',          # Blue for info
    'border': '#C8E6C9',        # Light green border
    'healthy': '#C8E6C9',       # Light green for healthy plants
    'warning_bg': '#FFF9C4',    # Light yellow for warning
    'critical_bg': '#FFCDD2',   # Light red for critical
}

# Configure ttk styles
def setup_styles():
    style = ttk.Style()
    style.theme_use('clam')
    
    # Main frame style
    style.configure('TFrame', background=COLORS['background'])
    style.configure('TLabelframe', background=COLORS['background'], 
                   foreground=COLORS['primary'], borderwidth=2, relief='solid')
    style.configure('TLabelframe.Label', background=COLORS['background'], 
                   foreground=COLORS['primary'], font=('Segoe UI', 11, 'bold'))
    
    # Button styles
    style.configure('Primary.TButton', 
                   background=COLORS['primary'],
                   foreground='white',
                   borderwidth=0,
                   focuscolor='none',
                   font=('Segoe UI', 10, 'bold'),
                   padding=8)
    style.map('Primary.TButton',
              background=[('active', COLORS['primary_dark']),
                         ('pressed', COLORS['primary_light'])])
    
    style.configure('Accent.TButton',
                   background=COLORS['accent'],
                   foreground='white',
                   borderwidth=0,
                   font=('Segoe UI', 10, 'bold'),
                   padding=8)
    style.map('Accent.TButton',
              background=[('active', '#F57C00'),
                         ('pressed', '#EF6C00')])
    
    style.configure('Danger.TButton',
                   background=COLORS['error'],
                   foreground='white',
                   borderwidth=0,
                   font=('Segoe UI', 10, 'bold'),
                   padding=8)
    style.map('Danger.TButton',
              background=[('active', '#C62828'),
                         ('pressed', '#B71C1C')])
    
    # Entry style
    style.configure('TEntry',
                   fieldbackground=COLORS['surface'],
                   foreground=COLORS['text'],
                   borderwidth=1,
                   relief='solid',
                   padding=5)
    
    # Combobox style
    style.configure('TCombobox',
                   fieldbackground=COLORS['surface'],
                   foreground=COLORS['text'],
                   padding=5)
    
    # Label style
    style.configure('TLabel',
                   background=COLORS['background'],
                   foreground=COLORS['text'],
                   font=('Segoe UI', 10))
    
    style.configure('Title.TLabel',
                   font=('Segoe UI', 16, 'bold'),
                   foreground=COLORS['primary'])
    
    style.configure('Subtitle.TLabel',
                   font=('Segoe UI', 11),
                   foreground=COLORS['text_secondary'])
    
    # Treeview style
    style.configure('Treeview',
                   background=COLORS['surface'],
                   foreground=COLORS['text'],
                   fieldbackground=COLORS['surface'],
                   borderwidth=1,
                   rowheight=28,
                   font=('Segoe UI', 9))
    style.configure('Treeview.Heading',
                   background=COLORS['primary'],
                   foreground='white',
                   relief='flat',
                   font=('Segoe UI', 10, 'bold'))
    style.map('Treeview.Heading',
              background=[('active', COLORS['primary_dark'])])
    
    # Scrollbar style
    style.configure('Vertical.TScrollbar',
                   background=COLORS['secondary'],
                   troughcolor=COLORS['background'],
                   borderwidth=0)
    style.configure('Horizontal.TScrollbar',
                   background=COLORS['secondary'],
                   troughcolor=COLORS['background'],
                   borderwidth=0)

# Plant model and other data structures
plant_model = {}
action_history = deque(maxlen=20)
auto_refresh_running = False
monitoring_thread = None

# -----------------------------
# PERCEPTION
# -----------------------------
def perceive(pid, leaf, moisture, temp):
    return {
        "plant_id": pid,
        "leaf_color": leaf,
        "moisture": moisture,
        "temperature": temp,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

# -----------------------------
# MODEL UPDATE
# -----------------------------
def update_model(p):
    pid = p["plant_id"]
    
    if pid in plant_model:
        action_history.append({
            "plant_id": pid,
            "state": plant_model[pid].copy()
        })
    
    if pid not in plant_model:
        plant_model[pid] = {
            "leaf_color": None,
            "moisture": None,
            "temperature": None,
            "last_leaf_color": None,
            "last_moisture": None,
            "last_temperature": None,
            "infection_history": [],
            "observation_history": [],
            "last_updated": None,
            "health_score": 100
        }
    
    s = plant_model[pid]
    
    s["observation_history"].append({
        "leaf_color": p["leaf_color"],
        "moisture": p["moisture"],
        "temperature": p["temperature"],
        "timestamp": p["timestamp"]
    })
    if len(s["observation_history"]) > 10:
        s["observation_history"].pop(0)
    
    s["last_leaf_color"] = s["leaf_color"]
    s["last_moisture"] = s["moisture"]
    s["last_temperature"] = s["temperature"]
    s["leaf_color"] = p["leaf_color"]
    s["moisture"] = p["moisture"]
    s["temperature"] = p["temperature"]
    s["last_updated"] = p["timestamp"]
    
    health_score = 100
    if s["leaf_color"] == "yellow":
        health_score -= 30
    elif s["leaf_color"] == "brown":
        health_score -= 60
    if s["moisture"] is not None:
        if s["moisture"] < 30 or s["moisture"] > 80:
            health_score -= 20
    if s["temperature"] is not None:
        if s["temperature"] < 10 or s["temperature"] > 35:
            health_score -= 25
    s["health_score"] = max(0, health_score)

# -----------------------------
# DECISION
# -----------------------------
def decide(pid):
    s = plant_model[pid]
    
    leaf = s["leaf_color"]
    last_leaf = s["last_leaf_color"]
    moisture = s["moisture"] if s["moisture"] is not None else 50
    temp = s["temperature"] if s["temperature"] is not None else 25
    history = s["infection_history"]
    
    if leaf == "brown":
        return "🚨 CRITICAL: Immediate repotting and pruning required"
    
    if moisture < 20:
        return "💧 URGENT: Severe dehydration - water immediately"
    
    if temp > 40:
        return "🔥 CRITICAL: Extreme heat - move to shade immediately"
    
    if temp < 5:
        return "❄️ CRITICAL: Freezing risk - move indoors"
    
    if last_leaf == "green" and leaf == "yellow":
        return "⚠️ Alert: Leaf deterioration detected - investigate cause"
    
    if "fungal" in history and leaf == "yellow":
        if moisture > 70:
            return "🍄 Fungal + overwatering: Apply antifungal and reduce watering"
        return "🍄 Apply targeted antifungal treatment"
    
    if "bacterial" in history and leaf == "yellow":
        return "🦠 Apply bactericide and remove affected leaves"
    
    if "pest" in history and leaf == "yellow":
        return "🐛 Apply pesticide and isolate plant"
    
    if leaf == "yellow":
        if moisture < 30:
            return "💧 Increase watering schedule"
        if moisture > 80:
            return "🌊 Reduce watering - possible root rot risk"
        if temp > 35:
            return "🌡️ Provide shade and cooling"
        if temp < 15:
            return "🌡️ Move to warmer location"
    
    if last_leaf == "yellow" and leaf == "green":
        return "✅ Plant improving - maintain current care"
    
    if leaf == "green" and moisture > 80:
        return "✅ Healthy but overwatered - reduce watering frequency"
    
    if leaf == "green" and moisture < 40:
        return "✅ Healthy but needs water soon"
    
    if leaf == "green":
        return "✅ Plant healthy - maintain current care"
    
    return "🔍 Monitor plant - no immediate action needed"

# -----------------------------
# UPDATE TABLE
# -----------------------------
def update_table():
    for row in tree.get_children():
        tree.delete(row)
    
    for pid, s in plant_model.items():
        health = s.get("health_score", 100)
        if health < 40:
            tag = "critical"
        elif health < 70:
            tag = "warning"
        else:
            tag = "healthy"
        
        # Add leaf emoji based on color
        leaf_emoji = ""
        if s["leaf_color"] == "green":
            leaf_emoji = "🌿"
        elif s["leaf_color"] == "yellow":
            leaf_emoji = "🍂"
        elif s["leaf_color"] == "brown":
            leaf_emoji = "🥀"
        
        color_display = f"{leaf_emoji} {s['leaf_color'] if s['leaf_color'] else '—'}"
        
        tree.insert("", "end", values=(
            f"🌱 {pid}",
            color_display,
            f"💧 {s['moisture'] if s['moisture'] is not None else '—'}%",
            f"🌡️ {s['temperature'] if s['temperature'] is not None else '—'}°C",
            f"{'⭐' * (health//20)} {health}%",
            get_trend_symbol(pid)
        ), tags=(tag,))
    
    tree.tag_configure("critical", background=COLORS['critical_bg'])
    tree.tag_configure("warning", background=COLORS['warning_bg'])
    tree.tag_configure("healthy", background=COLORS['healthy'])

def get_trend_symbol(pid):
    s = plant_model[pid]
    if s["last_leaf_color"] is None:
        return "➡️ Stable"
    if s["last_leaf_color"] == "green" and s["leaf_color"] == "yellow":
        return "📉 Declining"
    if s["last_leaf_color"] == "yellow" and s["leaf_color"] == "green":
        return "📈 Improving"
    return "➡️ Stable"

# -----------------------------
# SOUND ALERTS
# -----------------------------
def play_alert(action):
    if "CRITICAL" in action or "URGENT" in action:
        for _ in range(2):
            winsound.Beep(1000, 200)
            time.sleep(0.1)

# -----------------------------
# NOTIFICATIONS
# -----------------------------
def show_notification(plant_id, action):
    if "CRITICAL" in action or "URGENT" in action:
        notif = tk.Toplevel(root)
        notif.title("🚨 Plant Alert!")
        notif.geometry("350x120")
        notif.configure(bg=COLORS['error'])
        notif.transient(root)
        notif.grab_set()
        
        # Center the notification
        notif.update_idletasks()
        x = (notif.winfo_screenwidth() // 2) - (350 // 2)
        y = (notif.winfo_screenheight() // 2) - (120 // 2)
        notif.geometry(f"+{x}+{y}")
        
        tk.Label(notif, text="⚠️ URGENT PLANT ALERT ⚠️", 
                font=('Segoe UI', 12, 'bold'), bg=COLORS['error'], fg='white').pack(pady=10)
        tk.Label(notif, text=f"🌱 {plant_id}", 
                font=('Segoe UI', 10), bg=COLORS['error'], fg='white').pack()
        tk.Label(notif, text=action[:60], 
                font=('Segoe UI', 9), bg=COLORS['error'], fg='white').pack(pady=5)
        notif.after(3000, notif.destroy)

# -----------------------------
# ANIMATED AGENT STEP
# -----------------------------
def run_agent():
    pid = plant_id_entry.get().strip()
    if not pid:
        messagebox.showerror("Error", "Please enter a Plant ID", parent=root)
        return
    
    leaf = leaf_var.get().strip().lower()
    if leaf not in ["green", "yellow", "brown"]:
        messagebox.showerror("Error", "Leaf color must be green, yellow, or brown", parent=root)
        return
    
    try:
        moisture = int(moisture_entry.get())
        temp = int(temp_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for moisture and temperature", parent=root)
        return
    
    history_text = history_entry.get().strip()
    if history_text and pid in plant_model:
        plant_model[pid]["infection_history"] = [
            h.strip().lower() for h in history_text.split(",")
        ]
    elif history_text and pid not in plant_model:
        pass
    
    output_box.delete("1.0", tk.END)
    
    # Animated steps with colors
    output_box.insert(tk.END, "🌿 " + "="*60 + "\n", "title")
    output_box.insert(tk.END, "   MODEL-BASED AGENT EXECUTION\n", "title")
    output_box.insert(tk.END, "="*63 + "\n\n", "title")
    
    output_box.insert(tk.END, "🔍 STEP 1: PERCEPTION\n", "step")
    output_box.insert(tk.END, "   └─ Reading sensor data from environment...\n", "step_detail")
    root.update()
    time.sleep(0.3)
    
    p = perceive(pid, leaf, moisture, temp)
    output_box.insert(tk.END, f"   └─ 📊 Data: {p}\n\n", "data")
    
    output_box.insert(tk.END, "🧠 STEP 2: MODEL UPDATE\n", "step")
    output_box.insert(tk.END, "   └─ Updating internal state with new observations...\n", "step_detail")
    root.update()
    time.sleep(0.3)
    
    if pid not in plant_model and history_text:
        plant_model[pid] = {
            "leaf_color": None,
            "moisture": None,
            "temperature": None,
            "last_leaf_color": None,
            "last_moisture": None,
            "last_temperature": None,
            "infection_history": [h.strip().lower() for h in history_text.split(",")],
            "observation_history": [],
            "last_updated": None,
            "health_score": 100
        }
    
    update_model(p)
    health = plant_model[pid]['health_score']
    
    # Health bar visualization
    health_bar = "█" * (health // 10) + "░" * (10 - (health // 10))
    output_box.insert(tk.END, f"   └─ 🌡️ Health Score: {health}% {health_bar}\n", "data")
    output_box.insert(tk.END, f"   └─ 📈 Trend: {get_trend_symbol(pid)}\n\n", "data")
    
    update_table()
    
    output_box.insert(tk.END, "⚙️ STEP 3: DECISION MAKING\n", "step")
    output_box.insert(tk.END, "   └─ Analyzing model state against rules...\n", "step_detail")
    root.update()
    time.sleep(0.3)
    
    action = decide(pid)
    output_box.insert(tk.END, f"   └─ 🧠 Decision: {action}\n\n", "decision")
    
    output_box.insert(tk.END, "🚀 STEP 4: ACTION EXECUTION\n", "step")
    output_box.insert(tk.END, f"   └─ ✅ Executed: {pid} - {action}\n", "action")
    
    show_notification(pid, action)
    play_alert(action)
    
    # Configure text tags
    output_box.tag_config("title", foreground=COLORS['primary'], font=('Segoe UI', 11, 'bold'))
    output_box.tag_config("step", foreground=COLORS['accent'], font=('Segoe UI', 10, 'bold'))
    output_box.tag_config("step_detail", foreground=COLORS['text_secondary'], font=('Segoe UI', 9))
    output_box.tag_config("data", foreground=COLORS['info'], font=('Segoe UI', 9))
    output_box.tag_config("decision", foreground=COLORS['primary'], font=('Segoe UI', 10, 'bold'))
    output_box.tag_config("action", foreground=COLORS['success'], font=('Segoe UI', 10, 'bold'))
    
    output_box.see(tk.END)
    update_status(f"Completed: {action[:50]}")

# -----------------------------
# AUTO-REFRESH
# -----------------------------
def toggle_auto_refresh():
    global auto_refresh_running
    auto_refresh_running = not auto_refresh_running
    
    if auto_refresh_running:
        auto_refresh_btn.config(text="⏸️ Stop Auto-Refresh")
        auto_refresh_btn.configure(style='Accent.TButton')
        update_status("Auto-refresh started (every 5 seconds)")
        auto_refresh()
    else:
        auto_refresh_btn.config(text="▶️ Start Auto-Refresh")
        auto_refresh_btn.configure(style='Primary.TButton')
        update_status("Auto-refresh stopped")

def auto_refresh():
    if auto_refresh_running:
        if plant_id_entry.get().strip():
            run_agent()
        root.after(5000, auto_refresh)

# -----------------------------
# UNDO FUNCTIONALITY
# -----------------------------
def undo_last_action():
    if not action_history:
        messagebox.showinfo("Undo", "No actions to undo", parent=root)
        return
    
    last = action_history.pop()
    plant_id = last["plant_id"]
    plant_model[plant_id] = last["state"]
    update_table()
    output_box.insert(tk.END, f"↩️ Undid last action for {plant_id}\n", "action")
    output_box.see(tk.END)
    update_status(f"Undid last action for {plant_id}")

# -----------------------------
# CSV EXPORT
# -----------------------------
def export_csv():
    if not plant_model:
        messagebox.showwarning("Export", "No data to export", parent=root)
        return
    
    filename = f"plant_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Plant ID", "Timestamp", "Leaf Color", "Moisture", 
                        "Temperature", "Health Score", "Action"])
        
        for pid, s in plant_model.items():
            for obs in s["observation_history"]:
                action = decide(pid) if pid in plant_model else "Unknown"
                writer.writerow([
                    pid, obs["timestamp"], obs["leaf_color"],
                    obs["moisture"], obs["temperature"],
                    s["health_score"], action
                ])
    
    messagebox.showinfo("Export", f"✅ Data exported to {filename}", parent=root)
    update_status(f"Exported to {filename}")

# -----------------------------
# RESET FUNCTIONS
# -----------------------------
def reset_plant():
    pid = plant_id_entry.get().strip()
    if not pid:
        messagebox.showerror("Error", "Enter Plant ID to reset", parent=root)
        return
    
    if pid in plant_model:
        del plant_model[pid]
        update_table()
        output_box.insert(tk.END, f"✅ Reset all data for {pid}\n", "action")
        output_box.see(tk.END)
        messagebox.showinfo("Reset", f"Reset all data for {pid}", parent=root)
        update_status(f"Reset plant: {pid}")

def clear_all():
    if messagebox.askyesno("Clear All", "⚠️ Delete ALL plant data?\n\nThis action cannot be undone!", parent=root):
        plant_model.clear()
        action_history.clear()
        update_table()
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, "🗑️ All plant data has been cleared\n", "action")
        update_status("All data cleared")

# -----------------------------
# SEARCH/FILTER
# -----------------------------
def search_plant():
    query = search_entry.get().strip().lower()
    if not query:
        update_table()
        return
    
    for row in tree.get_children():
        tree.delete(row)
    
    for pid, s in plant_model.items():
        if query in pid.lower() or (s["leaf_color"] and query in s["leaf_color"].lower()):
            health = s.get("health_score", 100)
            if health < 40:
                tag = "critical"
            elif health < 70:
                tag = "warning"
            else:
                tag = "healthy"
            
            leaf_emoji = "🌿" if s["leaf_color"] == "green" else "🍂" if s["leaf_color"] == "yellow" else "🥀"
            color_display = f"{leaf_emoji} {s['leaf_color'] if s['leaf_color'] else '—'}"
            
            tree.insert("", "end", values=(
                f"🌱 {pid}",
                color_display,
                f"💧 {s['moisture'] if s['moisture'] is not None else '—'}%",
                f"🌡️ {s['temperature'] if s['temperature'] is not None else '—'}°C",
                f"{'⭐' * (health//20)} {health}%",
                get_trend_symbol(pid)
            ), tags=(tag,))

# -----------------------------
# GENERATE REPORT
# -----------------------------
def generate_report():
    report_window = tk.Toplevel(root)
    report_window.title("📋 Plant Health Report")
    report_window.geometry("600x500")
    report_window.configure(bg=COLORS['background'])
    
    # Center the window
    report_window.update_idletasks()
    x = (report_window.winfo_screenwidth() // 2) - (600 // 2)
    y = (report_window.winfo_screenheight() // 2) - (500 // 2)
    report_window.geometry(f"+{x}+{y}")
    
    title_label = tk.Label(report_window, text="🌿 PLANT HEALTH REPORT 🌿", 
                          font=('Segoe UI', 14, 'bold'), 
                          bg=COLORS['primary'], fg='white', pady=10)
    title_label.pack(fill=tk.X)
    
    report_text = tk.Text(report_window, wrap=tk.WORD, font=('Segoe UI', 10),
                         bg=COLORS['surface'], fg=COLORS['text'])
    scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=report_text.yview)
    report_text.configure(yscrollcommand=scrollbar.set)
    
    report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    report = f"""
{'='*60}
📅 DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 TOTAL PLANTS: {len(plant_model)}
{'='*60}

"""
    
    for pid, s in plant_model.items():
        health = s['health_score']
        if health >= 70:
            status_icon = "🟢"
        elif health >= 40:
            status_icon = "🟡"
        else:
            status_icon = "🔴"
            
        report += f"""
{status_icon} PLANT: {pid}
{'─'*50}
   📍 Health Score: {health}%
   🍃 Leaf Color: {s['leaf_color']}
   💧 Moisture: {s['moisture']}%
   🌡️ Temperature: {s['temperature']}°C
   🦠 Infections: {', '.join(s['infection_history']) if s['infection_history'] else 'None'}
   ⏰ Last Updated: {s['last_updated']}
   🎯 Recommended Action: {decide(pid)}
{'─'*50}
"""
    
    report_text.insert("1.0", report)
    report_text.config(state=tk.DISABLED)

# -----------------------------
# CREATE SCROLLABLE FRAME
# -----------------------------
def create_scrollable_frame(parent):
    canvas = tk.Canvas(parent, highlightthickness=0, bg=COLORS['background'])
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    return scrollable_frame, canvas, scrollbar

# -----------------------------
# UPDATE STATUS
# -----------------------------
def update_status(message):
    status_label.config(text=f"🌿 {message}")
    root.after(3000, lambda: status_label.config(text="🌿 Ready"))

# -----------------------------
# CREATE HEADER
# -----------------------------
def create_header(parent):
    header_frame = tk.Frame(parent, bg=COLORS['primary'], height=80)
    header_frame.pack(fill=tk.X)
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text="🌿 PLANT HEALTH MONITOR", 
                          font=('Segoe UI', 20, 'bold'), 
                          bg=COLORS['primary'], fg='white')
    title_label.pack(pady=15)
    
    subtitle_label = tk.Label(header_frame, text="Model-Based Agent System", 
                             font=('Segoe UI', 10), 
                             bg=COLORS['primary'], fg=COLORS['secondary'])
    subtitle_label.pack()

# -----------------------------
# GUI SETUP
# -----------------------------
root = tk.Tk()
root.title("🌿 Plant Health Monitor - Model-Based Agent")
root.geometry("1100x800")
root.configure(bg=COLORS['background'])

# Apply styles
setup_styles()

# Create header
create_header(root)

# Create main container with scrollbar
main_container = ttk.Frame(root)
main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

main_canvas = tk.Canvas(main_container, highlightthickness=0, bg=COLORS['background'])
main_scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=main_canvas.yview)
main_scrollable = ttk.Frame(main_canvas)

main_scrollable.bind(
    "<Configure>",
    lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
)

main_canvas.create_window((0, 0), window=main_scrollable, anchor="nw")
main_canvas.configure(yscrollcommand=main_scrollbar.set)

main_canvas.pack(side="left", fill="both", expand=True)
main_scrollbar.pack(side="right", fill="y")

# Bind mousewheel
def _on_mousewheel(event):
    main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

main_canvas.bind("<MouseWheel>", _on_mousewheel)

# ==================== INPUT SECTION ====================
input_frame = ttk.LabelFrame(main_scrollable, text="🌱 Plant Sensor Input", padding="15")
input_frame.pack(fill=tk.X, padx=10, pady=10)

# Configure grid weights
input_frame.columnconfigure(1, weight=1)

# Plant ID with icon
ttk.Label(input_frame, text="🌿 Plant ID:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=8, padx=5)
plant_id_entry = ttk.Entry(input_frame, width=30, font=('Segoe UI', 10))
plant_id_entry.grid(row=0, column=1, sticky=tk.W, pady=8, padx=5)

# Leaf Color with dropdown
ttk.Label(input_frame, text="🍃 Leaf Color:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=8, padx=5)
leaf_var = tk.StringVar(value="green")
leaf_dropdown = ttk.Combobox(input_frame, textvariable=leaf_var, 
                              values=["green", "yellow", "brown"], width=27, font=('Segoe UI', 10))
leaf_dropdown.grid(row=1, column=1, sticky=tk.W, pady=8, padx=5)

# Moisture with slider-like entry
ttk.Label(input_frame, text="💧 Moisture (%):", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=8, padx=5)
moisture_frame = ttk.Frame(input_frame)
moisture_frame.grid(row=2, column=1, sticky=tk.W, pady=8, padx=5)
moisture_entry = ttk.Entry(moisture_frame, width=15, font=('Segoe UI', 10))
moisture_entry.insert(0, "50")
moisture_entry.pack(side=tk.LEFT)
ttk.Label(moisture_frame, text=" (0-100)", foreground=COLORS['text_secondary']).pack(side=tk.LEFT, padx=5)

# Temperature
ttk.Label(input_frame, text="🌡️ Temperature (°C):", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=8, padx=5)
temp_frame = ttk.Frame(input_frame)
temp_frame.grid(row=3, column=1, sticky=tk.W, pady=8, padx=5)
temp_entry = ttk.Entry(temp_frame, width=15, font=('Segoe UI', 10))
temp_entry.insert(0, "25")
temp_entry.pack(side=tk.LEFT)
ttk.Label(temp_frame, text=" (-10 to 50)", foreground=COLORS['text_secondary']).pack(side=tk.LEFT, padx=5)

# Infection History
ttk.Label(input_frame, text="🦠 Infection History:", font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=8, padx=5)
history_entry = ttk.Entry(input_frame, width=30, font=('Segoe UI', 10))
history_entry.grid(row=4, column=1, sticky=tk.W, pady=8, padx=5)
ttk.Label(input_frame, text="(separate with commas: fungal, bacterial, pest)", 
          foreground=COLORS['text_secondary']).grid(row=4, column=2, sticky=tk.W, pady=8, padx=5)

# ==================== BUTTON SECTION ====================
button_frame = ttk.LabelFrame(main_scrollable, text="🎮 Control Panel", padding="15")
button_frame.pack(fill=tk.X, padx=10, pady=10)

button_row1 = ttk.Frame(button_frame)
button_row1.pack(fill=tk.X, pady=5)
button_row2 = ttk.Frame(button_frame)
button_row2.pack(fill=tk.X, pady=5)
button_row3 = ttk.Frame(button_frame)
button_row3.pack(fill=tk.X, pady=5)

# Row 1 buttons
ttk.Button(button_row1, text="▶ Run Agent Step", command=run_agent, style='Primary.TButton', width=20).pack(side=tk.LEFT, padx=5)
ttk.Button(button_row1, text="↩️ Undo Last Action", command=undo_last_action, style='Primary.TButton', width=20).pack(side=tk.LEFT, padx=5)
ttk.Button(button_row1, text="🔄 Reset Current Plant", command=reset_plant, style='Accent.TButton', width=20).pack(side=tk.LEFT, padx=5)
ttk.Button(button_row1, text="🗑️ Clear All Data", command=clear_all, style='Danger.TButton', width=20).pack(side=tk.LEFT, padx=5)

# Row 2 buttons
auto_refresh_btn = ttk.Button(button_row2, text="▶️ Start Auto-Refresh", command=toggle_auto_refresh, style='Primary.TButton', width=20)
auto_refresh_btn.pack(side=tk.LEFT, padx=5)
ttk.Button(button_row2, text="📄 Generate Report", command=generate_report, style='Primary.TButton', width=20).pack(side=tk.LEFT, padx=5)
ttk.Button(button_row2, text="💾 Export CSV", command=export_csv, style='Primary.TButton', width=20).pack(side=tk.LEFT, padx=5)

# Row 3 - Search
search_frame = ttk.Frame(button_row3)
search_frame.pack(fill=tk.X, pady=5)
ttk.Label(search_frame, text="🔍 Search Plants:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)
search_entry = ttk.Entry(search_frame, width=30, font=('Segoe UI', 10))
search_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(search_frame, text="Filter", command=search_plant, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
ttk.Button(search_frame, text="Show All", command=update_table, style='Primary.TButton').pack(side=tk.LEFT, padx=5)

# ==================== OUTPUT SECTION ====================
output_frame = ttk.LabelFrame(main_scrollable, text="📝 Agent Execution Log", padding="10")
output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

output_box = tk.Text(output_frame, height=14, wrap=tk.WORD, font=('Consolas', 9),
                     bg=COLORS['surface'], fg=COLORS['text'], 
                     selectbackground=COLORS['primary'], selectforeground='white')
output_scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=output_box.yview)
output_box.configure(yscrollcommand=output_scrollbar.set)

output_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# ==================== TABLE SECTION ====================
table_frame = ttk.LabelFrame(main_scrollable, text="📊 Plant Registry Dashboard", padding="10")
table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Create treeview with scrollbars
tree_container = ttk.Frame(table_frame)
tree_container.pack(fill=tk.BOTH, expand=True)

tree_scroll_y = ttk.Scrollbar(tree_container, orient="vertical")
tree_scroll_x = ttk.Scrollbar(tree_container, orient="horizontal")

columns = ("Plant ID", "Leaf Color", "Moisture", "Temperature", "Health", "Trend")
tree = ttk.Treeview(tree_container, columns=columns, show="headings",
                     yscrollcommand=tree_scroll_y.set,
                     xscrollcommand=tree_scroll_x.set,
                     height=8)

tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

# Configure column widths and alignment
column_widths = [180, 120, 100, 100, 150, 120]
for col, width in zip(columns, column_widths):
    tree.heading(col, text=col)
    tree.column(col, width=width, anchor='center')

tree.grid(row=0, column=0, sticky="nsew")
tree_scroll_y.grid(row=0, column=1, sticky="ns")
tree_scroll_x.grid(row=1, column=0, sticky="ew")

tree_container.grid_rowconfigure(0, weight=1)
tree_container.grid_columnconfigure(0, weight=1)

# ==================== STATUS BAR ====================
status_frame = tk.Frame(main_scrollable, bg=COLORS['primary'], height=30)
status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
status_frame.pack_propagate(False)

status_label = tk.Label(status_frame, text="🌿 Ready", font=('Segoe UI', 9),
                        bg=COLORS['primary'], fg='white', anchor=tk.W)
status_label.pack(fill=tk.X, padx=10, pady=5)

# Initial table update
update_table()

# Start the application
root.mainloop()