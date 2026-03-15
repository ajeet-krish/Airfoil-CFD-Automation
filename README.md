# Automated Airfoil-to-CFD Pipeline
**A high-fidelity bridge between geometric theory, CAD automation, and computational fluid dynamics.**

## 🚀 Overview
This project demonstrates an end-to-end automated engineering workflow designed to streamline the iterative design of aerodynamic profiles. By bridging Python-based geometry generation with OpenFOAM's simulation capabilities, this pipeline eliminates manual CAD bottlenecks and provides a repeatable framework for aerodynamic analysis.

### 📽️ Live Demonstration
#### Phase 1: Working GUI

![GUI Demo](media/GUI Interface.gif)
Description: Demonstration of the interactive GUI adjusting wing parameters. 

#### Phase 2: CAD Assembly Output
[INSERT SCREENSHOT: FreeCAD_Model_View.png]

---

## 🏗️ Project Plan
### Phase 1: Geometry Engine (`01_Geometry_Engine/`)
A Python-based utility that generates **NACA 4-digit airfoils** using the standard mean camber line and thickness distribution equations. 
- **Reactive UI**: Features a custom Tkinter interface with Bi-directional Constraint Solving. Adjusting chord, span, or aspect ratio (AR=b/c) automatically synchronizes the other two variables in real-time.
- **Data Export**: High-precision .dat coordinate export with metadata headers (NACA series, Chord, Span).
- **Planform Design (Work in progress)**: Support for both Rectangular and Delta (Triangle) wing shapes.

### Phase 2: Automated CAD Integration (`02_CAD_Integration/`)
A FreeCAD Python macro that consumes exported coordinates to generate a 3D wing section, ready for CFD analysis without manual user intervention.
- **Automated STL Library**: Automatically generates and saves .stl files to a dedicated library using professional naming conventions (e.g., naca_2412_span600mm.stl).
- **Live Link (Work in progress)**: Python script that enables background file-watching functionality for real-time CAD updates, eliminating the need to manually run the macro to generate the updated model.
- **Advanced Lofting (Work in progress)**: Lofting between root and tip profiles to support tapered and delta planforms.

### 3. High-Fidelity CFD (Next Step)
Computational Fluid Dynamics setup using the `simpleFoam` steady-state incompressible solver.
- **Meshing:** Background `blockMesh` with local surface refinement and boundary layer inflation via `snappyHexMesh`.

---

### 🛠️ Tools Involved
- **Languages:** Python (NumPy, Matplotlib, Tkinter, PySide)
- **CAD:** FreeCAD (Python API / Macros)
- **CFD:** OpenFOAM
- **Visualization:** ParaView & Matplotlib
- **Standards:** SI Units, NACA 4-Digit Equations

---

## 📊 Key Results (Work in Progress)
*Once simulations are run, this section will include:*
- **Pressure Distributions ($C_p$):** Visualizing the Bernoulli effect across the suction and pressure sides.
- **Velocity Contours:** Analyzing flow separation and stagnation points.
- **Performance Metrics:** Lift ($C_l$) and Drag ($C_d$) coefficients validated against experimental data.

---

## 🎓 Academic Context
Developed as a technical portfolio piece to demonstrate competence in **Mechanical Engineering** and **Aerodynamics**. This project applies principles of fluid mechanics to physical geometries through automated workflows.

---

## How to Run
1. **Generate**: Run `python 01_Geometry_Engine/generator.py`, adjust your wing parameters, and click **Update 3D Model**.
2. **Build**: In FreeCAD, run the build_airfoilCAD.py macro to generate the 3D geometry and the auto-named STL file.
3. **Verify**: Your production-ready STL will appear in 02_CAD_Integration/STL Files/.
