# Automated Airfoil-to-CFD Pipeline
**A high-fidelity bridge between geometric theory, CAD automation, and computational fluid dynamics.**

## 🚀 Overview
This project demonstrates an end-to-end automated engineering workflow designed to streamline the iterative design of aerodynamic profiles. By bridging Python-based geometry generation with OpenFOAM's simulation capabilities, this pipeline eliminates manual CAD bottlenecks and provides a repeatable framework for aerodynamic analysis.

### 🛠️ Tools Involved
- **Languages:** Python (NumPy, Matplotlib, Tkinter)
- **CAD:** FreeCAD (Python API / Macros)
- **CFD:** OpenFOAM
- **Visualization:** ParaView & Matplotlib
- **Standards:** SI Units, NACA 4-Digit Equations

---

## 🏗️ Project Plan
### 1. Geometry Engine (`01_Geometry_Engine/`)
A Python-based utility that generates **NACA 4-digit airfoils** using the standard Mean Camber Line and Thickness Distribution equations. 
- **Features:** GUI for rapid profile selection; high-precision `.dat` coordinate export (6 decimal places).

### 2. Automated CAD Integration (`02_CAD_Integration/`)
A FreeCAD Python macro that consumes exported coordinates to generate a 3D wing section.
- **Methodology:** Point-cloud import → B-Spline generation → Parametric extrusion.

### 3. High-Fidelity CFD (`03_OpenFOAM_Case/`)
Computational Fluid Dynamics setup using the `simpleFoam` steady-state incompressible solver.
- **Meshing:** Background `blockMesh` with local surface refinement and boundary layer inflation via `snappyHexMesh`.
- **Physics:** Turbulence modelling using Spalart-Allmaras or k-omega SST.

---

## 📊 Key Results (Work in Progress)
*Once simulations are run, this section will include:*
- **Pressure Distributions ($C_p$):** Visualizing the Bernoulli effect across the suction and pressure sides.
- **Velocity Contours:** Analyzing flow separation and stagnation points.
- **Performance Metrics:** Lift ($C_l$) and Drag ($C_d$) coefficients validated against experimental data (Abbott & Von Doenhoff).

---

## 🎓 Academic Context
Developed as a technical portfolio piece to demonstrate competence in **Mechanical Engineering** and **Aerodynamics**. This project applies principles of fluid mechanics and heat transfer to complex physical geometries.

## How to Run
1. Run `python 01_Geometry_Engine/generator.py` to create your airfoil.
2. Execute the FreeCAD macro to generate the `.stl` file.
3. Place the `.stl` in `03_OpenFOAM_Case/constant/triSurface/`.
4. Run `./Allrun` in the OpenFOAM directory.