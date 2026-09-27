import math

GM=4.9048e12
R=1737.4e3
altitude=500e3

r=R+altitude
v=math.sqrt(GM/r)
print(v)

print("Altitude (km) | Orbit speed (m/s)")
for altitude_km in [50, 100, 200, 500, 1000, 5000]:
    r=R+altitude_km * 1000
    v= math.sqrt(GM/r)
    print(altitude_km, "|", round(v))
