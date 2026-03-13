#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FreeCAD CAD Automation Script
Imports airfoil coordinates and generates a 3D wing section.
"""

import sys
import os
import glob
from typing import List

try:
    import FreeCAD as App
    import Part
    import Mesh
    import Draft
except ImportError:
    print("Error: FreeCAD Python API not found. Please run this inside FreeCAD or link the libraries.")
    sys.exit(1)

def import_airfoil_coordinates(dat_file: str) -> List[App.Vector]:
    """Reads airfoil coordinates from a .dat file.

    Args:
        dat_file: Path to the .dat file containing (x, y, z) coordinates.

    Returns:
        List[App.Vector]: A list of FreeCAD Vectors representing the profile.

    Raises:
        FileNotFoundError: If the dat_file does not exist.
        ValueError: If no valid points are found in the file.
    """
    if not os.path.exists(dat_file):
        raise FileNotFoundError(f"Coordinate file not found: {dat_file}")

    points: List[App.Vector] = []
    with open(dat_file, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                # Coordinate System: Chord (X), Lift (Y), Span (Z)
                x = float(parts[0])
                y = float(parts[1])
                z = float(parts[2]) if len(parts) > 2 else 0.0
                points.append(App.Vector(x, y, z))

    if not points:
        raise ValueError("No valid points found in the airfoil coordinate file.")

    # Ensure profile is closed for face creation
    if points[0].sub(points[-1]).Length > 1e-7:
        points.append(points[0])

    return points

def create_3d_wing(points: List[App.Vector], span: float = 2.0) -> Part.Feature:
    """Generates a 3D wing volume from profile points.

    Args:
        points: List of App.Vector points defining the airfoil profile.
        span: Length of the wing extrusion in meters (SI).

    Returns:
        Part.Feature: The generated wing object in the FreeCAD document.
    """
    # Create B-Spline using Part module
    curve = Part.BSplineCurve()
    curve.interpolate(points)
    edge = curve.toShape()
    wire = Part.Wire([edge])
    face = Part.Face(wire)

    # Extrude along Z-axis (Span direction per GEMINI.md)
    wing_shape = face.extrude(App.Vector(0, 0, span))

    doc = App.activeDocument() or App.newDocument("AirfoilWing")
    wing_obj = doc.addObject("Part::Feature", "WingSection")
    wing_obj.Shape = wing_shape
    
    doc.recompute()
    return wing_obj

def export_geometry(objects: List[Part.Feature], output_path: str) -> None:
    """Exports geometry to STL format for OpenFOAM snappyHexMesh.

    Args:
        objects: List of FreeCAD objects to export.
        output_path: Destination path for the .stl file.
    """
    Mesh.export(objects, output_path)
    print(f"Geometry successfully exported to: {output_path}")

def run_automation() -> None:
    """Orchestrates the airfoil-to-CAD pipeline."""
    try:
        # Find latest .dat file
        dat_files = glob.glob("*.dat")
        if not dat_files:
            print("Error: No .dat files found in root. Generate one first.")
            return

        latest_dat = max(dat_files, key=os.path.getctime)
        print(f"Processing: {latest_dat}")

        # 1. Import
        profile_points = import_airfoil_coordinates(latest_dat)

        # 2. Generate 3D Wing
        wing = create_3d_wing(profile_points, span=2.0)

        # 3. Export
        export_geometry([wing], "03_OpenFOAM_Case/constant/triSurface/airfoil_wing.stl")

    except Exception as e:
        print(f"Automation failed: {str(e)}")

if __name__ == "__main__":
    run_automation()
