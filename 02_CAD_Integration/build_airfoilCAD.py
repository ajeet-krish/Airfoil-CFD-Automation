import FreeCAD as App
import Part
import Mesh
import os
from PySide import QtCore

# --- Configuration ---
SOURCE_DAT = "/Users/ajeet/engineering/Projects/Airfoil_CFD_Automation/02_CAD_Integration/latest_airfoil.dat"
EXPORT_DIR = "/Users/ajeet/engineering/Projects/Airfoil_CFD_Automation/02_CAD_Integration/STL Files"

def export_to_stl(obj, naca_name, span_val):
    """Saves a separate STL file with a descriptive name."""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
    
    # Generate filename: e.g., naca_2412_span500mm.stl
    filename = f"naca{naca_name}_span{int(span_val*100)}mm.stl"
    save_path = os.path.join(EXPORT_DIR, filename)
    
    # Export the mesh (does not affect the GUI document)
    Mesh.export([obj], save_path)
    print(f"STL Exported to: {save_path}")

def update_model():
    if not os.path.exists(SOURCE_DAT):
        print(f"Error: Source file not found at {SOURCE_DAT}")
        return

    # 1. Access Document
    doc = App.ActiveDocument or App.newDocument("Airfoil_Model")
    
    points = []
    span_val = 1.0  # Span fallback default
    naca_name = "naca_custom" # Default
    
    # 2. Parce Source Data
    try:
        with open(SOURCE_DAT, "r") as f:
            for line in f:
                if line.startswith("# NACA:"):
                    naca_name = line.split(":")[1].strip()
                # Parse the span value calculated by the GUI
                elif line.startswith("# SPAN:"):
                    span_val = float(line.split(":")[1])
                elif not line.startswith("#"): # Skip other headers  
                    parts = line.split()
                    if len(parts) >= 2: # Ensure there are at least X and Y coordinates
                        # Convert m to mm
                        points.append(App.Vector(float(parts[0])*100, float(parts[1])*100, 0))
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 3. CRITICAL CHECK: Ensure we have enough points for a polygon
    if len(points) < 3:
        print(f"Error: Only {len(points)} points found. Need at least 3 to form an airfoil.")
        return

    # 4. Clear existing geometry only if we have new data to replace it
    for obj in doc.Objects:
        if obj.Name == "WingSection":
            doc.removeObject(obj.Name)

    # 5. Build the geometry
    extrusion_length = span_val * 100  # Calculate extrusion (Span converted to mm)
    wire = Part.makePolygon(points)
    face = Part.Face(wire)
    wing_shape = face.extrude(App.Vector(0, 0, extrusion_length))
    
    # Add to document
    wing_obj = doc.addObject("Part::Feature", "WingSection")
    wing_obj.Shape = wing_shape
    doc.recompute()

    # 6. Separate STL Export
    export_to_stl(wing_obj, naca_name, span_val)

    print(f"3D Model Wing successfully updated.")

# Execute
if __name__ == "__main__":
    update_model()