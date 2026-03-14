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
from tkinter import messagebox, ttk, filedialog
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
        self.b_slider, self.b_entry = self.create_input_pair("Span (b)", 0.1, 20.0, 5.0, "b", resolution=0.1)
        self.ar_slider, self.ar_entry = self.create_input_pair("Aspect Ratio", 1, 20, 5, "ar", resolution=0.5)

        # Action Buttons Section
        btn_frame = tk.Frame(self.ctrl_frame)
        btn_frame.pack(pady=10, fill=tk.X)
        
        tk.Button(btn_frame, text="Update 3D Model", command=self.export_dat, bg="#d1e7dd").pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Save .dat", command=self.save_custom_dat).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Save Plot (.png)", command=self.export_plot_image).pack(fill=tk.X, pady=2)

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

        # --- Reactive Math for Span, Chord, and Aspect Ratio ---
        # Fetch the current values to perform the update
        c = self.controls['c']['slider'].get()
        b = self.controls['b']['slider'].get()
        ar = self.controls['ar']['slider'].get()

        if key == 'c': # User changed Chord -> Update AR
            new_ar = b / c
            self.controls['ar']['slider'].set(new_ar)
            self.controls['ar']['entry_var'].set(f"{new_ar:.2f}")
        
        elif key == 'b': # User changed Span -> Update AR
            new_ar = b / c
            self.controls['ar']['slider'].set(new_ar)
            self.controls['ar']['entry_var'].set(f"{new_ar:.2f}")
            
        elif key == 'ar': # User changed AR -> Update Span
            new_b = ar * c
            self.controls['b']['slider'].set(new_b)
            self.controls['b']['entry_var'].set(f"{new_b:.2f}")

        self.update_plot()

    def sync_slider_from_entry(self, key):
        """Updates slider when text is manually entered."""
        try:
            val = float(self.controls[key]['entry_var'].get())
            slider = self.controls[key]['slider']
            # Clamp value to slider range
            val = max(slider.cget("from"), min(slider.cget("to"), val))
            slider.set(val)
            # Call the sync logic to update the related parameters
            self.sync_entry_from_slider(key)
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
        self.ax.set_title(f"NACA Airfoil")
        self.ax.set_xlabel("Chord (m)")
        self.ax.set_ylabel("Thickness (m)")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    def export_dat(self):
        """Overwrites the single airfoil file for CAD updates."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
    
        # Ensure the 02_CAD_Integration exists
        cad_dir = os.path.join(project_root, "02_CAD_Integration")
        os.makedirs(cad_dir, exist_ok=True)

        # Path to a singular, updating .dat file
        source_file = os.path.join(cad_dir, "latest_airfoil.dat")

        m = int(self.controls['m']['slider'].get())
        p = int(self.controls['p']['slider'].get())
        t = int(self.controls['t']['slider'].get())
        c = self.controls['c']['slider'].get()
        ar = self.controls['ar']['slider'].get()

        # Calculate span based on Aspect Ratio
        span = ar * c
        
        # ... (Get m, p, t, c from sliders) ...
        xu, yu, xl, yl = generate_naca_airfoil(m, p, t, c)
        
        try:
            with open(source_file, "w") as f:
                # FreeCAD reads header
                f.write(f"# CHORD:{c}\n")
                f.write(f"# SPAN:{span}\n")
                # Write to the same file every time
                for i in range(len(xu)-1, 0, -1):
                    f.write(f"{xu[i]:.6f} {yu[i]:.6f} 0.0\n")
                for i in range(len(xl)):
                    f.write(f"{xl[i]:.6f} {yl[i]:.6f} 0.0\n")
            messagebox.showinfo("Success", "Updated latest_airfoil.dat for CAD refresh")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update source: {e}")
    
    def export_plot_image(self):
        """Prompts user to select destination for the plot image."""
        m, p, t = int(self.controls['m']['slider'].get()), int(self.controls['p']['slider'].get()), int(self.controls['t']['slider'].get())
        default_filename = f"plot_naca_{m}{p}{t:02d}.png"
        
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        
        if file_path:
            self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {file_path}")

    def save_custom_dat(self):
        """Prompts user to select destination for the custom .dat file."""
        m, p, t = int(self.controls['m']['slider'].get()), int(self.controls['p']['slider'].get()), int(self.controls['t']['slider'].get())
        default_filename = f"naca_{m}{p}{t:02d}.dat"
        
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".dat",
            filetypes=[("DAT files", "*.dat")]
        )
        
        if file_path:
            xu, yu, xl, yl = generate_naca_airfoil(
                self.controls['m']['slider'].get(),
                self.controls['p']['slider'].get(),
                self.controls['t']['slider'].get(),
                self.controls['c']['slider'].get()
            )
            with open(file_path, "w") as f:
                for i in range(len(xu)-1, 0, -1):
                    f.write(f"{xu[i]:.6f} {yu[i]:.6f} 0.0\n")
                for i in range(len(xl)):
                    f.write(f"{xl[i]:.6f} {yl[i]:.6f} 0.0\n")
            print(f"Data saved to: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AirfoilGUI(root)
    root.mainloop()

# %%
