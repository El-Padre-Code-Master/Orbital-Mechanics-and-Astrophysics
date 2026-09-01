import math

#PHYSICAL CONSTANTS
G = 6.67430e-11        # Gravitational constant
C = 299792458          # Speed of light
M_SUN = 1.989e30       # Mass of the Sun
HBAR = 1.054571817e-34 # Reduced Planck constant
K_B = 1.380649e-23     # Boltzmann constant

def calculate_black_hole_properties(mass_kg):
    #Schwarzschild Radius
    r_s = (2 * G * mass_kg) / (C**2)
    
    #Photon Sphere
    r_photon = 1.5 * r_s
    
    #Innermost Stable Circular Orbit
    r_isco = 3.0 * r_s
    
    #Hawking Temperature 
    t_hawking = (HBAR * (C**3)) / (8 * math.pi * G * mass_kg * K_B)
    
    #Evaporation Lifetime
    lifetime_sec = (5120 * math.pi * (G**2) * (mass_kg**3)) / (HBAR * (C**4))
    lifetime_years = lifetime_sec / (365.25 * 24 * 3600)

    return {
        "r_s_km": r_s / 1000.0,
        "r_photon_km": r_photon / 1000.0,
        "r_isco_km": r_isco / 1000.0,
        "t_hawking_k": t_hawking,
        "lifetime_years": lifetime_years
    }

def main():
    print("==================================================")
    print("               BLACK HOLE CALCULATOR              ")
    print("==================================================")
    print("1. Enter Mass in Solar Masses (M☉)")
    print("2. Enter Mass in Kilograms (kg)")
    
    choice = input("Select input option (1 or 2) [Default = 1]: ").strip()
    
    if choice == "2":
        try:
            mass_kg = float(input("\nEnter Mass (kg): "))
            mass_sun = mass_kg / M_SUN
        except ValueError:
            print("Invalid mass. Defaulting to 10 Solar Masses.")
            mass_sun = 10.0
            mass_kg = mass_sun * M_SUN
    else:
        user_in = input("\nEnter Mass (Solar Masses) [Default = 10]: ").strip()
        try:
            mass_sun = float(user_in) if user_in else 10.0
        except ValueError:
            mass_sun = 10.0
        mass_kg = mass_sun * M_SUN

    results = calculate_black_hole_properties(mass_kg)

    print("\n--------------------------------------------------")
    print(f" INPUT MASS            : {mass_sun:,.2f} Solar Masses ({mass_kg:.3e} kg)")
    print("--------------------------------------------------")
    print(f" Schwarzschild Radius  : {results['r_s_km']:.2f} km")
    print(f" Light Horizon (Photon Sphere): {results['r_photon_km']:.2f} km")
    print(f" ISCO Orbit Radius     : {results['r_isco_km']:.2f} km")
    print(f" Escape Velocity at Horizon  : 299,792.458 km/s (c)")
    print(f" Hawking Temperature   : {results['t_hawking_k']:.3e} K")
    print(f" Evaporation Lifetime  : {results['lifetime_years']:.3e} Years")
    print("--------------------------------------------------\n")

if __name__ == "__main__":
    main()