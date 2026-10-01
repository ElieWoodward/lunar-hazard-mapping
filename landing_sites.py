import numpy as np
import rasterio
import matplotlib.pyplot as plt
from scipy.ndimage import binary_erosion

def load_map(path):
    with rasterio.open(path) as src:
        return src.read(1)

elevation = load_map("data/Site01_final_adj_5mpp_surf.tif")
dz_dy, dz_dx = np.gradient(elevation, 5)
slope = np.degrees(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))
safe = slope < 10

radius_px = 5
y, x = np.ogrid[-radius_px:radius_px + 1, -radius_px:radius_px + 1]
window = x**2 + y**2 <= radius_px**2

landable = binary_erosion(safe, structure=window)

for zone_m in [20, 50, 100, 200, 400]:
    r = zone_m // 2 // 5
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    window = x**2 + y**2 <= r**2
    landable = binary_erosion(safe, structure=window)
    print(zone_m, "m zone:", round(landable.mean() * 100, 2), "%")

fig, axes = plt.subplots(1, 2)
axes[0].imshow(safe, cmap="RdYlGn", extent=[0, 16, 16, 0])
axes[0].set_title("Slope under 10 deg")
axes[1].imshow(landable, cmap="RdYlGn", extent=[0, 16, 16, 0])
axes[1].set_title("Landable 50 m zone")
plt.show()