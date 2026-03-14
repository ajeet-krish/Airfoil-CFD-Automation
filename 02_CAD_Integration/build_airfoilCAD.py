import FreeCAD as App
import Part
import os
from PySide import QtCore

# Set absolute path to the source airfoil file
SOURCE_DAT = "/Users/ajeet/engineering/Projects/Airfoil_CFD_Automation/02_CAD_Integration/latest_airfoil.dat"

def update_model():
    if not os.path.exists(SOURCE_DAT):
        print(f"Error: Source file not found at {SOURCE_DAT}")
        return

    # 1. Access Document
    doc = App.ActiveDocument or App.newDocument("Airfoil_Model")
    points = []
    span_val = 5.0  # Span fallback default
    
    # 2. Read and Build with Validation
    points = []
    try:
        with open(SOURCE_DAT, "r") as f:
            for line in f:
                # Parse the span value calculated by the GUI
                if line.startswith("# SPAN:"):
                    span_val = float(line.split(":")[1])
                    continue
                if line.startswith("#"): # Skip other headers
                    continue
                
                parts = line.split()
                if len(parts) >= 2: # Ensure there are at least X and Y coordinates
                    # Convert m to mm
                    points.append(App.Vector(float(parts[0])*100, float(parts[1])*100, 0))
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Convert span to mm for FreeCAD extrusion
    extrusion_length = span_val * 100

    # 3. CRITICAL CHECK: Ensure we have enough points for a polygon
    if len(points) < 3:
        print(f"Error: Only {len(points)} points found. Need at least 3 to form an airfoil.")
        return

    # 4. Clear existing geometry only if we have new data to replace it
    for obj in doc.Objects:
        doc.removeObject(obj.Name)

    # 5. Build the geometry
    wire = Part.makePolygon(points)
    face = Part.Face(wire)
    extrusion = face.extrude(App.Vector(0, 0, extrusion_length))
    
    # 6. Finalize
    wing = doc.addObject("Part::Feature", "WingSection")
    wing.Shape = extrusion
    doc.recompute()
    print("3D Model successfully updated.")

update_model()