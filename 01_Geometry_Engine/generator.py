#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airfoil Geometry Generator with Interactive GUI, Text Inputs, and Presets
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox, ttk

def generate_naca_airfoil(m, p, t, c, n_points=100):
    """
    m: max camber (percentage of chord)
    p: position of max camber (tens of percent of chord)
    t: max thickness (percentage of chord)
    c: chord length
    """
    m = m / 100.0
    p = p / 10.0
    t = t / 100.0
    x = np.linspace(0, c, n_points)
    x_norm = x / c
    yt = 5 * t * c * (0.2969 * np.sqrt(x_norm) - 0.1260 * x_norm - 0.3516 * x_norm**2 + 0.2843 * x_norm**3 - 0.1015 * x_norm**4)
    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)

    for i in range(len(x)):
        xi = x[i] / c
        if xi <= p:
            if p > 0:
                yc[i] = (m * c / p**2) * (2 * p * xi - xi**2)
                dyc_dx[i] = (2 * m / p**2) * (p - xi)
        else:
            if p < 1:
                yc[i] = (m * c / (1 - p)**2) * ((1 - 2 * p) + 2 * p * xi - xi**2)
                dyc_dx[i] = (2 * m / (1 - p)**2) * (p - xi)

    theta = np.arctan(dyc_dx)
    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    return xu, yu, xl, yl

class AirfoilGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NACA Airfoil Engine - Interactive")
        
        # Presets Data
        self.presets = {
            "NACA 0012": (0.0, 0.0, 12.0, 1.0),
            "NACA 2412": (2.0, 4.0, 12.0, 1.0),
            "NACA 4412": (4.0, 4.0, 12.0, 1.0),
            "NACA 2415": (2.0, 4.0, 15.0, 1.0),
            "NACA 6412": (6.0, 4.0, 12.0, 1.0)
        }

        # Main frames
        self.ctrl_frame = tk.Frame(root)
        self.ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.plot_frame = tk.Frame(root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Preset Selection
        tk.Label(self.ctrl_frame, text="NACA Presets:").pack(anchor=tk.W)
        self.preset_var = tk.StringVar(value="Select Preset")
        self.preset_menu = ttk.Combobox(self.ctrl_frame, textvariable=self.preset_var, values=list(self.presets.keys()), state="readonly")
        self.preset_menu.pack(fill=tk.X, pady=(0, 15))
        self.preset_menu.bind("<<ComboboxSelected>>", self.apply_preset)

        # Sliders and Entry Boxes
        self.controls = {}
        self.m_slider, self.m_entry = self.create_input_pair("Max Camber (%)", 0, 9.5, 2.0, "m")
        self.p_slider, self.p_entry = self.create_input_pair("Max Camber Pos (x10%)", 0, 9, 4, "p")
        self.t_slider, self.t_entry = self.create_input_pair("Max Thickness (%)", 1, 40, 12, "t")
        self.c_slider, self.c_entry = self.create_input_pair("Chord Length", 0.1, 10.0, 1.0, "c", resolution=0.1)

        # Export Button
        self.btn_export = tk.Button(self.ctrl_frame, text="Export .dat", command=self.export_dat)
        self.btn_export.pack(pady=20)

        # Plotting Setup
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.update_plot()

    def create_input_pair(self, label, min_val, max_val, default, key, resolution=0.5):
        frame = tk.Frame(self.ctrl_frame)
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(frame, text=label).pack(anchor=tk.W)
        
        # Sub-frame for slider and entry side-by-side
        sub_frame = tk.Frame(frame)
        sub_frame.pack(fill=tk.X)
        
        slider = tk.Scale(sub_frame, from_=min_val, to=max_val, 
                         orient=tk.HORIZONTAL, resolution=resolution,
                         command=lambda x: self.sync_entry_from_slider(key))
        slider.set(default)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        entry_var = tk.StringVar(value=str(default))
        entry = tk.Entry(sub_frame, textvariable=entry_var, width=6)
        entry.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Bindings for text entry
        entry.bind("<Return>", lambda e: self.sync_slider_from_entry(key))
        entry.bind("<FocusOut>", lambda e: self.sync_slider_from_entry(key))
        
        self.controls[key] = {'slider': slider, 'entry_var': entry_var}
        return slider, entry

    def sync_entry_from_slider(self, key):
        val = self.controls[key]['slider'].get()
        self.controls[key]['entry_var'].set(f"{val:.2f}" if key == 'c' else f"{val:.1f}")
        self.update_plot()

    def sync_slider_from_entry(self, key):
        try:
            val = float(self.controls[key]['entry_var'].get())
            slider = self.controls[key]['slider']
            # Clamp value to slider range
            val = max(slider.cget("from"), min(slider.cget("to"), val))
            slider.set(val)
            self.update_plot()
        except ValueError:
            # Revert to slider value on invalid input
            self.sync_entry_from_slider(key)

    def apply_preset(self, event):
        preset_name = self.preset_var.get()
        if preset_name in self.presets:
            m, p, t, c = self.presets[preset_name]
            self.controls['m']['slider'].set(m)
            self.controls['p']['slider'].set(p)
            self.controls['t']['slider'].set(t)
            self.controls['c']['slider'].set(c)
            # update_plot is triggered by slider.set() via command binding

    def update_plot(self):
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
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    def export_dat(self):
        m = int(self.controls['m']['slider'].get())
        p = int(self.controls['p']['slider'].get())
        t = int(self.controls['t']['slider'].get())
        c = self.controls['c']['slider'].get()
        
        xu, yu, xl, yl = generate_naca_airfoil(m, p, t, c)
        filename = f"naca_{m}{p}{t:02d}.dat"
        
        try:
            with open(filename, "w") as f:
                for i in range(len(xu)-1, 0, -1):
                    f.write(f"{xu[i]:.6f} {yu[i]:.6f} 0.0\012")
                for i in range(len(xl)):
                    f.write(f"{xl[i]:.6f} {yl[i]:.6f} 0.0\012")
            messagebox.showinfo("Success", f"Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AirfoilGUI(root)
    root.mainloop()
