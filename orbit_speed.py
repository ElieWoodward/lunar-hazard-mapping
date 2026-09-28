import math

GM = 4.9048e12
R = 1737.4e3

def orbit_speed(altitude_km):
    r = R + altitude_km * 1000
    return math.sqrt(GM / r)

def orbit_period(altitude_km):
    r = R + altitude_km * 1000
    return (2 * math.pi * r) / orbit_speed(altitude_km)

def orbit_period_kepler(altitude_km):
    r = R + altitude_km * 1000
    return 2 * math.pi * math.sqrt(r**3 / GM)

print(orbit_period(100) / 60, "minutes (distance / speed)")
print(orbit_period_kepler(100) / 60, "minutes (Kepler)")
print(math.isclose(orbit_period(100), orbit_period_kepler(100)))

    
