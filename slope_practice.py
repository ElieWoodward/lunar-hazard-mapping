import numpy as np

terrain = np.array([
    [100, 102, 105],
    [ 98, 100, 110],
    [ 95,  97, 120],
])

dz_dy, dz_dx = np.gradient(terrain, 5)
steepness = np.sqrt(dz_dx**2 + dz_dy**2)
angle = np.degrees(np.arctan(steepness))

print(dz_dx[1, 1], dz_dy[1, 1])
print(angle[1, 1])