import numpy as np

terrain = np.array([
    [100, 102, 105],
    [ 98, 100, 110],
    [ 95,  97, 120],
])

print(terrain.shape)
print(terrain[0, 2])
print(terrain.max())
print(terrain.max() - terrain.min())
