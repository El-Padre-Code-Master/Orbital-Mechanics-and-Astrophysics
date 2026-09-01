import math

# Universal Constants & Planetary Parameters
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)

PLANETS = {
    "Earth": {"mass": 5.972e24, "radius": 6371000},   # Mass in kg, Radius in meters
    "Mars":  {"mass": 6.417e23, "radius": 3389500},
    "Moon":  {"mass": 7.342e22, "radius": 1737400}
}

def calculate_orbital_physics(planet_name, altitude_km, launch_velocity_km_s):
    planet = PLANETS[planet_name]
    M = planet["mass"]
    r = planet["radius"] + (altitude_km * 1000)  # Total distance from planetary center
    v_launch = launch_velocity_km_s * 1000        # Convert km/s to m/s

    # Standard Orbital Velocity: v = sqrt(G * M / r)
    v_orbit = math.sqrt((G * M) / r)
    
    # Escape Velocity: v_esc = sqrt(2 * G * M / r)
    v_escape = math.sqrt(2) * v_orbit

    print(f"\n=================== LAUNCH ANALYSIS: {planet_name.upper()} ===================")
    print(f"Target Altitude   : {altitude_km:,} km")
    print(f"Required Circular Orbital Velocity : {v_orbit / 1000:.2f} km/s ({v_orbit * 3600 / 1000:.0f} km/h)")
    print(f"Required Planetary Escape Velocity : {v_escape / 1000:.2f} km/s ({v_escape * 3600 / 1000:.0f} km/h)")
    print(f"Your Actual Rocket Velocity        : {launch_velocity_km_s:.2f} km/s")
    print("----------------------------------------------------------------------")

    # Evaluate trajectory
    if v_launch < v_orbit:
        deficit = (v_orbit - v_launch) / 1000
        print(f"RESULT: SUB-ORBITAL TRAJECTORY ❌")
        print(f"--> Insufficient velocity! Additional velocity required +{deficit:.2f} km/s.")
    elif math.isclose(v_launch, v_orbit / 1000, abs_tol=0.1):
        print(f"RESULT: STABLE CIRCULAR ORBIT ACHIEVED! 🛰️")
        print(f"--> Perfect balance! Gravity acts as centripetal force without pulling the craft down.")
    elif v_launch < v_escape:
        print(f"RESULT: ELLIPTICAL ORBIT ACHIEVED 🔄")
        print(f"--> Orbit reached! Your apogee will extend far into space.")
    else:
        print(f"RESULT: ESCAPE TRAJECTORY (HYPERBOLIC) 🌌")
        print(f"--> You broke free of {planet_name}'s gravity well entirely! Heading into deep space.")
    print("======================================================================\n")

# Run a test launch (Planet, Target Altitude in km, Rocket Speed in km/s)
# Earth Low Orbit (~400 km like the ISS) requires ~7.66 km/s
calculate_orbital_physics(planet_name="Earth", altitude_km=400, launch_velocity_km_s=7.66)