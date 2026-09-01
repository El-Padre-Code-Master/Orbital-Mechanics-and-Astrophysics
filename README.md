# Orbital Mechanics and Astrophysics

A collection of Python tools designed to calculate and visualize interplanetary orbital mechanics, spacecraft telemetry and much more. Built with `numpy`, `matplotlib`, `scipy`, and `PyQt5`.

## Included Scripts

### 1. orbit_sim.py — Terminal Orbital Velocity Calculator
A fast, lightweight tool for calculating essential orbital parameters for satellite and spacecraft trajectories.

* **Features:**
  * Calculates standard orbital velocity for circular and elliptical orbits around celestial bodies.
  * Computes escape velocity and orbital period.
  * Supports custom planetary constants (Earth, Mars, Moon, Sun) and user-defined altitudes.

### 2. space_transfer_3D.py — 3D Interplanetary Transfer Visualizer
An interactive 3D orbital mechanics simulation modeling a Hohmann Transfer Orbit from Earth to Mars.

* **Features:**
  * **Accurate Astrodynamics:** Models planetary orbital angular velocities and computes exact phase alignment angles.
  * **Optimal Launch Window Finder:** Calculates the specific launch departure day required to achieve a precise intercept with Mars.
  * **Dynamic Telemetry:** Real-time overlay displaying departure $\Delta v$, Mars capture insertion burn, transit time, and alignment error.
  * **Real-Time Trajectory Tracking:** Features dynamic path tracing behind the spacecraft without looping, along with a custom restart control.

### 3. black_hole_calculator.py — Computing Black Hole Properties
A tool for computing key relativistic parameters for Schwarzschild black holes based on Solar Masses or kilograms.

* **Features:**
  * Calculates Schwarzschild radius ($r_s$), escape velocity, and photon sphere/light horizon.
  * **Example:** $\text{Mass} = 10 \, M_{\odot} \implies r_s \approx 29.5 \text{ km}$.

### 4. NASA_interplanetary_mission_designer.py — NASA GMAT/JPL Style Mission Designer
A GUI-based astrodynamics workspace utilizing Keplerian conic solvers and Lambert arc generation to model multi-leg interplanetary missions with gravity assists.

* **Features:**
  * **Interactive GUI:** Real-time adjustments via departure sliders and Time-of-Flight controls for multi-leg transfer trajectories.
  * **Dual-Pane Visualization:** Features a 3D Heliocentric Ecliptic Trajectory Plot paired with an interactive Porkchop Contour plot ($C_3$ characteristic energy optimization).
  * **Left-Panel Telemetry:** Live HUD panel featuring high-visibility monospaced typography detailing real-time parameters (departure, capture, total mission) and flight duration.

### 5. star_classifier.py — Stellar Spectral & Luminosity Classifier
An astrophysics utility that classifies stars along the Morgan-Keenan spectral sequence and plots them on Hertzsprung-Russell diagrams.

* **Features:**
  * **Spectral & Temperature Mapping:** Maps effective surface temperature, color index, and absolute magnitude to stellar classes.
  * **H-R Diagram Generation:** Renders interactive Hertzsprung-Russell plots highlighting the Main Sequence, Red Giants, Supergiants, and White Dwarfs.
  * **Stellar Parameter Estimations:** Calculates stellar luminosity, radius, and estimated main-sequence lifetime.

---

## 🛠️ Prerequisites & Installation

Ensure you have Python 3.8+ installed along with the required scientific and GUI libraries:

```bash
pip install numpy matplotlib scipy pyqt5
