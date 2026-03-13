import FreeCAD as App
import Part
import os

# --- Configuration ---
dat_file = "../01_Geometry_Engine/naca_2412.dat" # Update to dynamic path if needed
thickness = 100.0  # Extrusion length in mm

def create_airfoil_part(file_path, length):
    # 1. Read coordinates from your generated .dat file
    points = []
    with open(file_path, "r") as f:
        for line in f:
            coords = [float(x) for x in line.split()]
            # Scale coordinates by a factor (e.g., 100mm chord)
            points.append(App.Vector(coords[0]*100, coords[1]*100, 0))

    # 2. Create the wire/profile
    wire = Part.makePolygon(points)
    face = Part.Face(wire)

    # 3. Extrude along the Z-axis
    extrusion = face.extrude(App.Vector(0, 0, length))
    
    # 4. Save/Export to .stl for OpenFOAM
    extrusion.exportStep("airfoil_part.step")
    extrusion.exportStl("airfoil.stl")
    
    # Add to document
    doc = App.ActiveDocument
    obj = doc.addObject("Part::Feature", "AirfoilWing")
    obj.Shape = extrusion
    doc.recompute()
    print("Airfoil 3D Model generated and exported to .stl")

create_airfoil_part(dat_file, thickness)