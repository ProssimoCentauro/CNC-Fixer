import re
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import sys

if getattr(sys, 'frozen', False):
    app_dir = os.path.dirname(sys.executable)
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))

conf_dir = os.path.join(app_dir, "conf")
if not os.path.exists(conf_dir):
    try:
        os.makedirs(conf_dir)
    except Exception as e:
        print(f"Error creating conf directory: {e}")

SETTINGS_FILE = os.path.join(conf_dir, "backlash_fixer_settings.json")

def estrai_coordinate(linea):
    x = y = z = None
    if 'X' in linea:
        x_match = re.search(r'X(-?\d+\.\d+)', linea)
        if x_match:
            x = float(x_match.group(1))
    if 'Y' in linea:
        y_match = re.search(r'Y(-?\d+\.\d+)', linea)
        if y_match:
            y = float(y_match.group(1))
    if 'Z' in linea:
        z_match = re.search(r'Z(-?\d+\.\d+)', linea)
        if z_match:
            z = float(z_match.group(1))
    return x, y, z

def sostituisci_coordinate(linea, nuova_x, nuova_y, nuova_z):
    if nuova_x is not None:
        linea = re.sub(r'X(-?\d+\.\d+)', f"X{nuova_x:.3f}", linea)
    if nuova_y is not None:
        linea = re.sub(r'Y(-?\d+\.\d+)', f"Y{nuova_y:.3f}", linea)
    if nuova_z is not None:
        linea = re.sub(r'Z(-?\d+\.\d+)', f"Z{nuova_z:.3f}", linea)
    return linea

def scegli_file():
    filepath = filedialog.askopenfilename(filetypes=[("G-code files", "*.nc"), ("All files", "*.*")])
    if filepath:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, filepath)
        save_settings()

def applica_backlash():
    try:
        offset_x = float(entry_x.get())
        offset_y = float(entry_y.get())
        offset_z = float(entry_z.get())
    except ValueError:
        messagebox.showerror("Error!", "Please enter valid numeric values for offsets.")
        return

    filepath = entry_file.get()
    if not filepath:
        messagebox.showerror("Error!", "Please select a '.nc' file first.")
        return

    try:
        prev_x = prev_y = prev_z = None
        dir_x = dir_y = dir_z = 0

        new_lines = []
        with open(filepath, "r") as infile:
            for linea in infile:
                x, y, z = estrai_coordinate(linea)

                new_x, new_y, new_z = x, y, z

                if x is not None and prev_x is not None:
                    nuova_dir_x = 1 if x > prev_x else -1 if x < prev_x else 0
                    if dir_x != 0 and nuova_dir_x != dir_x:
                        new_x += offset_x * nuova_dir_x
                    dir_x = nuova_dir_x
                if x is not None:
                    prev_x = x

                if y is not None and prev_y is not None:
                    nuova_dir_y = 1 if y > prev_y else -1 if y < prev_y else 0
                    if dir_y != 0 and nuova_dir_y != dir_y:
                        new_y += offset_y * nuova_dir_y
                    dir_y = nuova_dir_y
                if y is not None:
                    prev_y = y

                if z is not None and prev_z is not None:
                    nuova_dir_z = 1 if z > prev_z else -1 if z < prev_z else 0
                    if dir_z != 0 and nuova_dir_z != dir_z:
                        new_z += offset_z * nuova_dir_z
                    dir_z = nuova_dir_z
                if z is not None:
                    prev_z = z

                nuova_linea = sostituisci_coordinate(linea, new_x, new_y, new_z)
                new_lines.append(nuova_linea)

        output_path = filepath.replace(".nc", "_FIXED.nc")
        with open(output_path, "w") as outfile:
            outfile.writelines(new_lines)

        save_settings()
        
        messagebox.showinfo("Done!", f"File saved as:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error!", f"An error occurred:\n{str(e)}")

def save_settings():
    settings = {
        "last_file": entry_file.get(),
        "offset_x": entry_x.get(),
        "offset_y": entry_y.get(),
        "offset_z": entry_z.get()
    }
    
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Error saving settings: {e}")

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "last_file": "",
            "offset_x": "0.02",
            "offset_y": "0.02",
            "offset_z": "0.01"
        }
    
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {
            "last_file": "",
            "offset_x": "0.02",
            "offset_y": "0.02",
            "offset_z": "0.01"
        }

root = tk.Tk()
root.title("CNC Backlash Fixer")

settings = load_settings()

tk.Label(root, text="Select G-code file (.nc):").grid(row=0, column=0, sticky="w")
entry_file = tk.Entry(root, width=40)
entry_file.insert(0, settings["last_file"])
entry_file.grid(row=1, column=0, padx=5, pady=5)
tk.Button(root, text="Browse...", command=scegli_file).grid(row=1, column=1, padx=5)

tk.Label(root, text="Offset X:").grid(row=2, column=0, sticky="w")
entry_x = tk.Entry(root)
entry_x.insert(0, settings["offset_x"])
entry_x.grid(row=3, column=0, padx=5)

tk.Label(root, text="Offset Y:").grid(row=4, column=0, sticky="w")
entry_y = tk.Entry(root)
entry_y.insert(0, settings["offset_y"])
entry_y.grid(row=5, column=0, padx=5)

tk.Label(root, text="Offset Z:").grid(row=6, column=0, sticky="w")
entry_z = tk.Entry(root)
entry_z.insert(0, settings["offset_z"])
entry_z.grid(row=7, column=0, padx=5)

tk.Button(root, text="Apply Backlash Fix", command=applica_backlash, bg="lightgreen").grid(row=8, column=0, columnspan=2, pady=10)

root.protocol("WM_DELETE_WINDOW", lambda: [save_settings(), root.destroy()])

root.mainloop()