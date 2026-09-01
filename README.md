# Orbital Mechanics and Astrophysics

A collection of Python tools designed to calculate and visualize interplanetary orbital mechanics, Hohmann transfer orbits, and spacecraft telemetry. Built with `numpy` and `matplotlib`.


### 1. `orbit_sim.py` — Terminal Orbital Velocity Calculator
A fast, lightweight tool for calculating essential orbital parameters for satellite and spacecraft trajectories.

* **Features:**
  * Calculates standard orbital velocity for circular and elliptical orbits around celestial bodies.
  * Computes escape velocity and orbital period.
  * Supports custom planetary constants (Earth, Mars, Moon, Sun) and user-defined altitudes.

### 2. `space_transfer_3D.py` — 3D Interplanetary Transfer Visualizer
An interactive 3D orbital mechanics simulation modeling a **Hohmann Transfer Orbit** from Earth to Mars.

* **Features:**
  * **Accurate Astrodynamics:** Models planetary orbital angular velocities and computes exact phase alignment angles.
  * **Optimal Launch Window Finder:** Calculates the specific launch departure day required to achieve a precise intercept with Mars.
  * **Dynamic Telemetry:** Real-time overlay displaying departure delta-v, Mars capture insertion burn, transit time, and alignment error.
  * **Real-Time Trajectory Tracking:** Features dynamic path tracing behind the spacecraft without looping, along with a custom restart control.


### 2. `black_hole_calculator.py` — Computing black hole properties

* **Features:**
  * **Easy tool for computing black hole properties** based on Solar Masses or kilograms: Schwarzschild radius, Escape velocity, Light horizon
  * Example: Mass = 10 Suns → Radius ≈ 29.5 km

## 🛠️ Prerequisites & Installation

Ensure you have Python installed along with the required scientific libraries:

```bash
pip install numpy matplotlib
