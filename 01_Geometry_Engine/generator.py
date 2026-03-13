#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airfoil Geometry Generator with Interactive GUI, Text Inputs, and Presets
Demonstrates aerodynamic coordinate generation and CAD export automation.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox, ttk
import os
from naca_math import generate_naca_airfoil # Importing the math module

class AirfoilGUI:
    """
    Tkinter-based Graphical User Interface for real-time airfoil manipulation.
    Handles user inputs, triggers plot updates, and manages file export.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("NACA Airfoil Engine - Interactive")
        
        # Pre-defined geometry libraries for standard testing
        self.presets = {
            "NACA 0012": (0.0, 0.0, 12.0, 1.0),
            "NACA 2412": (2.0, 4.0, 12.0, 1.0),
            "NACA 4412": (4.0, 4.0, 12.0, 1.0),
            "NACA 2415": (2.0, 4.0, 15.0, 1.0),
            "NACA 6412": (6.0, 4.0, 12.0, 1.0)
        }

        # --- UI Layout Initialization ---
        self.ctrl_frame = tk.Frame(root)
        self.ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.plot_frame = tk.Frame(root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Preset Dropdown Menu
        tk.Label(self.ctrl_frame, text="NACA Presets:").pack(anchor=tk.W)
        self.preset_var = tk.StringVar(value="Select Preset")
        self.preset_menu = ttk.Combobox(self.ctrl_frame, textvariable=self.preset_var, values=list(self.presets.keys()), state="readonly")
        self.preset_menu.pack(fill=tk.X, pady=(0, 15))
        self.preset_menu.bind("<<ComboboxSelected>>", self.apply_preset)

        # Dynamic Sliders & Entry Box Generation
        self.controls = {}
        self.m_slider, self.m_entry = self.create_input_pair("Max Camber (%)", 0, 9.5, 2.0, "m")
        self.p_slider, self.p_entry = self.create_input_pair("Max Camber Pos (x10%)", 0, 9, 4, "p")
        self.t_slider, self.t_entry = self.create_input_pair("Max Thickness (%)", 1, 40, 12, "t")
        self.c_slider, self.c_entry = self.create_input_pair("Chord Length", 0.1, 10.0, 1.0, "c", resolution=0.1)

        # Export Action Button
        self.btn_export = tk.Button(self.ctrl_frame, text="Export .dat", command=self.export_dat)
        self.btn_export.pack(pady=20)

        # --- Matplotlib Canvas Setup ---
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize the plot with default values
        self.update_plot()

    def create_input_pair(self, label, min_val, max_val, default, key, resolution=0.5):
        """Helper to create synchronized slider and text entry widgets."""
        frame = tk.Frame(self.ctrl_frame)
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(frame, text=label).pack(anchor=tk.W)
        
        # Sub-frame for slider and entry side-by-side
        sub_frame = tk.Frame(frame)
        sub_frame.pack(fill=tk.X)
        
        # Slider configuration
        slider = tk.Scale(sub_frame, from_=min_val, to=max_val, 
                         orient=tk.HORIZONTAL, resolution=resolution,
                         command=lambda x: self.sync_entry_from_slider(key))
        slider.set(default)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Text entry configuration
        entry_var = tk.StringVar(value=str(default))
        entry = tk.Entry(sub_frame, textvariable=entry_var, width=6)
        entry.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Bind text input events to update the slider
        entry.bind("<Return>", lambda e: self.sync_slider_from_entry(key))
        entry.bind("<FocusOut>", lambda e: self.sync_slider_from_entry(key))
        
        self.controls[key] = {'slider': slider, 'entry_var': entry_var}
        return slider, entry

    def sync_entry_from_slider(self, key):
        """Updates text box when slider is dragged."""
        val = self.controls[key]['slider'].get()
        self.controls[key]['entry_var'].set(f"{val:.2f}" if key == 'c' else f"{val:.1f}")
        self.update_plot()

    def sync_slider_from_entry(self, key):
        """Updates slider when text is manually entered."""
        try:
            val = float(self.controls[key]['entry_var'].get())
            slider = self.controls[key]['slider']
            # Clamp value to slider range
            val = max(slider.cget("from"), min(slider.cget("to"), val))
            slider.set(val)
            self.update_plot()
        except ValueError:
            # Revert to valid slider value if user types text/invalid characters
            self.sync_entry_from_slider(key)

    def apply_preset(self, event):
        """Populates UI controls from predefined NACA library."""
        preset_name = self.preset_var.get()
        if preset_name in self.presets:
            m, p, t, c = self.presets[preset_name]
            self.controls['m']['slider'].set(m)
            self.controls['p']['slider'].set(p)
            self.controls['t']['slider'].set(t)
            self.controls['c']['slider'].set(c)

    def update_plot(self):
        """Fetches current UI values, calculates geometry, and redraws the Matplotlib canvas."""
        m = self.controls['m']['slider'].get()
        p = self.controls['p']['slider'].get()
        t = self.controls['t']['slider'].get()
        c = self.controls['c']['slider'].get()

        xu, yu, xl, yl = generate_naca_airfoil(m, p, t, c)

        self.ax.clear()
        self.ax.plot(xu, yu, 'b-', label='Upper Surface')
        self.ax.plot(xl, yl, 'r-', label='Lower Surface')
        self.ax.set_aspect('equal')
        self.ax.set_title(f"Interactive NACA Profile")
        self.ax.set_xlabel("Chord (m)")
        self.ax.set_ylabel("Thickness (m)")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    def export_dat(self):
        # 1. Get the directory where 'generator.py' is currently located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 2. Get the Project Root (by going up one level from the script)
        project_root = os.path.dirname(script_dir)
        # 3. Join that to the target folder
        target_dir = os.path.join(project_root, "02_CAD_Integration", "Airfoil Files")
    
        # Ensure the directory exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        m = int(self.controls['m']['slider'].get())
        p = int(self.controls['p']['slider'].get())
        t = int(self.controls['t']['slider'].get())
        c = self.controls['c']['slider'].get()
        
        xu, yu, xl, yl = generate_naca_airfoil(m, p, t, c)

        # Format filename to standard NACA designation
        filename = f"naca_{m}{p}{t:02d}.dat"
        full_path = os.path.join(target_dir, filename)
        
        try:
            with open(full_path, "w") as f:
                # CAD requires a continuous loop: Trailing Edge -> Upper -> Leading Edge -> Lower -> Trailing Edge
                for i in range(len(xu)-1, 0, -1):
                    f.write(f"{xu[i]:.6f} {yu[i]:.6f} 0.0\012")
                for i in range(len(xl)):
                    f.write(f"{xl[i]:.6f} {yl[i]:.6f} 0.0\012")
            messagebox.showinfo("Success", f"{filename} exported to {target_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AirfoilGUI(root)
    root.mainloop()

# %%
