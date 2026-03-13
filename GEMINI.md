# Gemini Instructions: Airfoil-to-CFD Pipeline

## Project Overview
This project is an end-to-end automated pipeline for airfoil design and analysis. It bridges Python (Geometry), FreeCAD (CAD), and OpenFOAM (CFD).

## Project Structure
- **01_Geometry_Engine/**: Python logic & GUI
- **02_CAD_Integration/**: FreeCAD Macros (.FCMacro)
- **03_OpenFOAM_Case/**: Simulation setup (0, constant, system)
- **04_Visualization/**: ParaView states & exported CSVs
- **docs/**: Theory and Validation

## Engineering Standards
- **Coding:** Python 3.10+, NumPy, Type Hints, Google-style docstrings.
- **Units:** SI Units strictly (m, s, kg, Pa).
- **Coordinate System:** Chord along X-axis, Span along Z-axis, Lift along Y-axis.
- **Precision:** Float64 / 6 decimal places for geometry.
- **Git:** Use Conventional Commits for all summaries.

## Tool-Specific Rules
1. **FreeCAD:** Use the `Part` and `Draft` modules. Avoid the GUI-specific `Gui` module in scripts where possible to allow for headless execution.
2. **OpenFOAM:** Target ESI-OpenCFD versioning. Ensure `boundaryField` names are consistent across `0/` files.
3. **Math:** Refer to Anderson's *Fundamentals of Aerodynamics* for all coefficient derivations.
