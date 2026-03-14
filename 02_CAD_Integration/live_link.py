import FreeCAD as App
import Part
import os
from PySide import QtCore

# Set absolute path to the 'Source of Truth'
SOURCE_DAT = "/Users/ajeet/engineering/Projects/Airfoil_CFD_Automation/02_CAD_Integration/latest_airfoil.dat"

# Global variables to keep the timer running in the background
global file_watcher_timer
global last_mtime

def update_model():
    """Your proven geometry generation logic."""
    doc = App.ActiveDocument or App.newDocument("Airfoil_Model")
    
    points = []
    try:
        with open(SOURCE_DAT, "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    points.append(App.Vector(float(parts[0])*100, float(parts[1])*100, 0))
    except Exception as e:
        return

    if len(points) < 3:
        return

    # Clear old geometry
    for obj in doc.Objects:
        doc.removeObject(obj.Name)

    # Build new geometry
    wire = Part.makePolygon(points)
    face = Part.Face(wire)
    extrusion = face.extrude(App.Vector(0, 0, 100.0))
    
    wing = doc.addObject("Part::Feature", "WingSection")
    wing.Shape = extrusion
    doc.recompute()

def check_for_updates():
    """Checks if the file has been modified since the last check."""
    global last_mtime
    try:
        # Get the current "last modified" timestamp of the file
        current_mtime = os.path.getmtime(SOURCE_DAT)
        
        # If the timestamp has changed, the GUI just exported a new file!
        if current_mtime != last_mtime:
            last_mtime = current_mtime
            App.Console.PrintMessage("File change detected. Rebuilding geometry...\n")
            update_model()
    except OSError:
        pass # File might be briefly locked by the OS while the GUI is writing to it

def start_live_link():
    global file_watcher_timer
    global last_mtime
    
    if not os.path.exists(SOURCE_DAT):
        App.Console.PrintError("Error: Run the Python GUI and export first.\n")
        return
        
    last_mtime = os.path.getmtime(SOURCE_DAT)
    
    # If a timer is already running, stop it to prevent duplicates
    if 'file_watcher_timer' in globals():
        file_watcher_timer.stop()
        
    # Start a background timer that triggers every 1000 ms (1 second)
    file_watcher_timer = QtCore.QTimer()
    file_watcher_timer.timeout.connect(check_for_updates)
    file_watcher_timer.start(1000) 
    
    App.Console.PrintMessage("Live Link Active: Watching latest_airfoil.dat for changes...\n")
    
    # Run once immediately to sync up
    update_model()

# Execute the listener
start_live_link()