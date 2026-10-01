import numpy as np
import rasterio

def load_map(path):
    with rasterio.open(path) as src:
        return src.read(1)

elevation = load_map("data/Site01_final_adj_5mpp_surf.tif")
nasa_slope = load_map("data/Site01_final_adj_5mpp_slp.tif")

dz_dy, dz_dx = np.gradient(elevation, 5)
my_slope = np.degrees(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))

difference = my_slope - nasa_slope
print("Average difference:", np.abs(difference).mean(), "degrees")
print("Biggest difference:", np.abs(difference).max(), "degrees")

abs_diff = np.abs(difference)

row, col = np.unravel_index(np.argmax(abs_diff), abs_diff.shape)
print("Biggest difference is at row", row, "column", col)

inner = abs_diff[1:-1, 1:-1]
print("Biggest difference without edges:", inner.max(), "degrees")

import matplotlib.pyplot as plt

safe = my_slope < 10
safe[0, :] = False
safe[-1, :] = False
safe[:, 0] = False
safe[:, -1] = False

print(safe.mean() * 100, "% of the area is under 10 degrees")

plt.imshow(safe, cmap="RdYlGn", extent=[0, 16, 16, 0])
plt.title("Site01 landing safety (green = under 10 degrees)")
plt.show()