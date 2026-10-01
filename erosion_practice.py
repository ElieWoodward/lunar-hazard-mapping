import numpy as np
from scipy.ndimage import binary_erosion

safe_small = np.array([
    [1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1],
    [1, 1, 0, 1, 1],
    [1, 1, 1, 1, 1],
], dtype=bool)

window = np.ones((3, 3), dtype=bool)
result = binary_erosion(safe_small, structure=window)

print(result.astype(int))