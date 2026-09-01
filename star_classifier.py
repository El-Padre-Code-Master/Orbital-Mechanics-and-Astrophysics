def classify_spectral_class(temp):
    """Determines the spectral class based on surface temperature (Kelvin)."""
    if temp >= 30000:
        return 'O'
    elif temp >= 10000:
        return 'B'
    elif temp >= 7500:
        return 'A'
    elif temp >= 6000:
        return 'F'
    elif temp >= 5200:
        return 'G'
    elif temp >= 3700:
        return 'K'
    elif temp >= 2400:
        return 'M'
    else:
        return 'L/T Subdwarf'

def classify_star(temp, lum):
    """Determines evolutionary position on the Hertzsprung-Russell Diagram."""
    spectral_type = classify_spectral_class(temp)
    
    # 1. White Dwarfs
    if lum <= 0.01 and temp >= 4000:
        evolutionary_type = "White Dwarf"
        description = "Dense, hot degenerate stellar core remaining after low/intermediate mass star death."
        
    # 2. Supergiants
    elif lum >= 10000:
        if temp < 4000:
            evolutionary_type = "Red Supergiant"
        elif temp > 10000:
            evolutionary_type = "Blue Supergiant"
        else:
            evolutionary_type = "Yellow Supergiant"
        description = "High-mass star undergoing advanced nuclear fusion stages near the end of its lifespan."
        
    # 3. Giants
    elif lum >= 10 and temp < 6000:
        evolutionary_type = "Red Giant"
        description = "Evolved star that has exhausted core hydrogen and expanded significantly."
        
    # 4. Main Sequence: Standard core hydrogen-burning stars (following HR relation)
    # Luminosity scales roughly with temperature: L ~ T^4 to T^8 along the main band
    elif (temp >= 5200 and temp <= 6000 and 0.5 <= lum <= 1.5) or \
         (temp > 6000 and lum > 1.5) or \
         (temp < 5200 and lum < 0.5):
        evolutionary_type = "Main Sequence Star (V)"
        description = "Stable star actively fusing hydrogen into helium in its core."
        
    else:
        evolutionary_type = "Subgiant / Transition Phase"
        description = "Star moving off the Main Sequence toward the Giant Branch."

    return spectral_type, evolutionary_type, description

def main():
    print("==================================================")
    print("       HERTZSPRUNG-RUSSELL STAR CLASSIFIER        ")
    print("==================================================")
    
    try:
        temp_input = input("Enter Surface Temperature (K) [e.g., 5800]: ").strip()
        temp = float(temp_input) if temp_input else 5800.0
        
        lum_input = input("Enter Luminosity (L/L_sun) [e.g., 1.0]: ").strip()
        lum = float(lum_input) if lum_input else 1.0
    except ValueError:
        print("\nInvalid input. Defaulting to Sun parameters (5800 K, 1.0 L/L_sun).")
        temp, lum = 5800.0, 1.0

    spec_class, evo_type, desc = classify_star(temp, lum)

    print("\n--------------------------------------------------")
    print(f" INPUT PARAMETERS : {temp:,.0f} K | {lum:,.4f} L/L_sun")
    print("--------------------------------------------------")
    print(f" Spectral Class   : {spec_class}-type")
    print(f" Star Type        : {evo_type}")
    print(f" Stellar Profile  : {desc}")
    print("--------------------------------------------------\n")

if __name__ == "__main__":
    main()