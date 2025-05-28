import serial
import tkinter as tk
from tkinter import ttk
import threading
import json
import os

PORT = 'COM9'
BAUD = 9600
MAX_SENSORS = 6
REF_VOLTAGE = 5.0
LABELS_FILE = "sensor_labels.json"
LIMITS_FILE = "sensor_limits.json"
CONFIG_FILE = "sensor_config.json"

# === Load/Save helpers ===
def load_json_file(filename, default):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return default

def save_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

label_texts = load_json_file(LABELS_FILE, [f"Photodiode {i+1}" for i in range(MAX_SENSORS)])
voltage_limits = load_json_file(LIMITS_FILE, [{"min": None, "max": None} for _ in range(MAX_SENSORS)])
config = load_json_file(CONFIG_FILE, {"selected_indices": list(range(MAX_SENSORS))})

def save_labels(): save_json_file(LABELS_FILE, label_texts)
def save_limits(): save_json_file(LIMITS_FILE, voltage_limits)
def save_config(): save_json_file(CONFIG_FILE, config)

# === SERIAL SETUP ===
ser = serial.Serial(PORT, BAUD, timeout=1)

# === GUI SETUP ===
root = tk.Tk()
root.title("Photodiode Monitor")

top_frame = ttk.Frame(root, padding="10")
top_frame.grid(row=0, column=0, sticky="ew")

main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=1, column=0)

label_vars = []
value_vars = []
value_labels = []

def refresh_gui():
    for widget in main_frame.winfo_children():
        widget.destroy()
    label_vars.clear()
    value_vars.clear()
    value_labels.clear()

    for idx in config["selected_indices"]:
        # Sensor label
        var = tk.StringVar(value=label_texts[idx])
        lbl = ttk.Label(main_frame, textvariable=var, foreground="black", cursor="hand2", font=("Segoe UI", 12))
        lbl.grid(row=idx, column=0, sticky="W", padx=5, pady=5)
        lbl.bind("<Double-Button-1>", lambda e, index=idx: edit_label(e, index))
        label_vars.append(var)

        # Voltage display
        val_var = tk.StringVar(value="--- V")
        val_lbl = tk.Label(main_frame, textvariable=val_var, font=("Segoe UI", 12, "bold"), width=10, relief="sunken", bg="yellow")
        val_lbl.grid(row=idx, column=1, padx=5, pady=5)
        value_vars.append(val_var)
        value_labels.append(val_lbl)

        # Range button
        btn = ttk.Button(main_frame, text="Set Range", command=lambda index=idx: edit_limits(index))
        btn.grid(row=idx, column=2, padx=5)

def edit_label(event, index):
    def save_edit(event=None):
        new_label = entry.get().strip()
        if new_label:
            label_texts[index] = new_label
            save_labels()
            refresh_sensor_selector()
            refresh_gui()
        entry.destroy()

    entry = tk.Entry(main_frame)
    entry.insert(0, label_texts[index])
    entry.grid(row=index, column=0, sticky="W", padx=5)
    entry.bind("<Return>", save_edit)
    entry.bind("<FocusOut>", save_edit)
    entry.focus()

def edit_limits(index):
    popup = tk.Toplevel(root)
    popup.title(f"Set Limits for {label_texts[index]}")
    popup.geometry("250x100")

    tk.Label(popup, text="Min V:").grid(row=0, column=0, padx=5, pady=5)
    tk.Label(popup, text="Max V:").grid(row=1, column=0, padx=5, pady=5)

    min_var = tk.StringVar(value=str(voltage_limits[index].get("min", "")))
    max_var = tk.StringVar(value=str(voltage_limits[index].get("max", "")))

    tk.Entry(popup, textvariable=min_var).grid(row=0, column=1, padx=5)
    tk.Entry(popup, textvariable=max_var).grid(row=1, column=1, padx=5)

    def save_and_close():
        try:
            voltage_limits[index]["min"] = float(min_var.get())
        except ValueError:
            voltage_limits[index]["min"] = None
        try:
            voltage_limits[index]["max"] = float(max_var.get())
        except ValueError:
            voltage_limits[index]["max"] = None
        save_limits()
        popup.destroy()

    tk.Button(popup, text="Save", command=save_and_close).grid(row=2, column=0, columnspan=2, pady=10)

# === Dropdown-style multi-select for sensors ===
dropdown_btn = ttk.Menubutton(top_frame, text="Select Sensors", direction='below')
dropdown_btn.grid(row=0, column=0, padx=5, pady=5)

menu = tk.Menu(dropdown_btn, tearoff=False)
dropdown_btn['menu'] = menu

sensor_vars = [tk.BooleanVar(value=(i in config["selected_indices"])) for i in range(MAX_SENSORS)]

def refresh_sensor_selector():
    menu.delete(0, 'end')
    for i in range(MAX_SENSORS):
        menu.add_checkbutton(label=label_texts[i], variable=sensor_vars[i], command=update_selected_sensors)

def update_selected_sensors():
    config["selected_indices"] = [i for i, var in enumerate(sensor_vars) if var.get()]
    save_config()
    refresh_gui()

refresh_sensor_selector()

# === Update Values ===
# diplays real time values from arduino. Displays  the values as green if in range, red if out of range and yellow if no range is set
def update_values():
    while True:
        try:
            line = ser.readline().decode().strip()
            values = list(map(int, line.split(',')))
            if len(values) != MAX_SENSORS:
                continue
            voltages = [v * REF_VOLTAGE / 1023 for v in values]
            for i, idx in enumerate(config["selected_indices"]):
                value_vars[i].set(f"{voltages[idx]:.2f} V")
                v = voltages[idx]
                lim = voltage_limits[idx]
                if lim["min"] is not None and lim["max"] is not None:
                    if lim["min"] <= v <= lim["max"]:
                        value_labels[i].config(bg="lightgreen")
                    else:
                        value_labels[i].config(bg="tomato")
                else:
                    value_labels[i].config(bg="yellow")
        except Exception:
            continue

refresh_gui()
threading.Thread(target=update_values, daemon=True).start()
root.mainloop()
