# Gemini Instructions: Airfoil-to-CFD Pipeline

## Project Overview
This project is an end-to-end automated pipeline for airfoil design and analysis. It bridges Python (Geometry Engine with Reactive UI), FreeCAD (Automated CAD & STL generation), and OpenFOAM (CFD). Phases 1 and 2 are functionally complete; the current focus is Phase 3 (OpenFOAM mesh generation and simulation).

## Project Structure
- **01_Geometry_Engine/**: Python logic & Tkinter GUI (`generator.py`, `naca_math.py`). Generates parameter-driven `.dat` files.
- **02_CAD_Integration/**: FreeCAD Macros (`build_airfoilCAD.py`). Contains the `STL Files/` directory for automated mesh library exports.
- **03_OpenFOAM_Case/**: Simulation setup (`0/`, `constant/`, `system/`).
- **04_Visualization/**: ParaView states & exported CSVs.
- **docs/**: Theory, Validation, and Media assets (GIFs/Videos).

## Engineering Standards
- **Coding:** Python 3.10+, NumPy, Matplotlib, Tkinter. Type Hints, Google-style docstrings.
- **UI/UX:** Utilize Bi-directional Constraint Solving for interrelated aerodynamic variables (e.g., mathematically synchronizing Aspect Ratio, Span, and Chord in real-time).
- **Units:** SI Units strictly (m, s, kg, Pa) in Python and CFD. *Note: The FreeCAD macro explicitly scales meters to millimeters (1:100) for CAD workspace visibility, then OpenFOAM scales it back if necessary.*
- **Coordinate System:** Chord along X-axis, Span along Z-axis, Lift along Y-axis.
- **Precision:** Float64 / 6 decimal places for geometry coordinates.
- **Git:** Use Conventional Commits for all summaries.

## Tool-Specific Rules
1. **Data Transfer (Python -> CAD):** The exported `.dat` file MUST include string-formatted metadata headers (e.g., `# NACA:`, `# SPAN:`, `# TAPER:`) to pass parametric instructions from the GUI to the CAD engine.
2. **FreeCAD Architecture:** * Use the `Part` module for solid B-Rep generation (polygons, faces, extrusions, lofts).
    * Use the `Mesh` module exclusively for tessellation and STL export. 
    * Overwrite the `WingSection` object in the Active Document to keep the GUI clean, but separate the STL export process to build a persistent file library.
3. **File Naming:** Enforce strict nomenclature for exported meshes to allow for future CFD scripting: `naca_[naca_name]_span[span_in_mm]mm.stl` (e.g., `naca_2412_span600mm.stl`).
4. **OpenFOAM:** Target ESI-OpenCFD versioning. Ensure `boundaryField` names are consistent across `0/` files. Use `surfaceFeatureExtract` to preserve sharp trailing edges on imported STLs.
5. **Math:** Refer to Anderson's *Fundamentals of Aerodynamics* for all coefficient derivations.
