import numpy as np
import rasterio
import matplotlib.pyplot as plt
from scipy.ndimage import binary_erosion, distance_transform_edt

ELEVATION_FILE = "data/Site01_final_adj_5mpp_surf.tif"
PIXEL_M = 5
SLOPE_LIMIT_DEG = 10

def load_map(path):
    with rasterio.open(path) as src:
        return src.read(1)

def compute_slope(elevation, pixel_m):
    dz_dy, dz_dx = np.gradient(elevation, pixel_m)
    return np.degrees(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))

def mark_edges_unsafe(safe):
    result = safe.copy()
    result[0, :] = False
    result[-1, :] = False
    result[:, 0] = False
    result[:, -1] = False
    return result

def circle_window(radius_px):
    y, x = np.ogrid[-radius_px:radius_px + 1, -radius_px:radius_px + 1]
    return x**2 + y**2 <= radius_px**2

elevation = load_map(ELEVATION_FILE)
slope = compute_slope(elevation, PIXEL_M)
safe = mark_edges_unsafe(slope < SLOPE_LIMIT_DEG)

rows,cols = elevation.shape
width_km = cols* PIXEL_M/1000
height_km = rows* PIXEL_M/1000
extent = [0, width_km, height_km, 0]

print("Under", SLOPE_LIMIT_DEG, "deg:", round(safe.mean() * 100, 2), "%")

for zone_m in [20, 50, 100, 200, 400]:
    r = zone_m // 2 // PIXEL_M
    landable = binary_erosion(safe, structure=circle_window(r))
    print(zone_m, "m zone:", round(landable.mean() * 100, 2), "%")

clearance_m = distance_transform_edt(safe) * PIXEL_M
row, col = np.unravel_index(np.argmax(clearance_m), clearance_m.shape)
x_km = col * PIXEL_M / 1000
y_km = row * PIXEL_M / 1000

print("Best site:", x_km, "km across,", y_km, "km down")
print("Distance to nearest hazard:", clearance_m.max(), "m")

plt.imshow(clearance_m, cmap="viridis", extent=extent)
plt.colorbar(label="Distance to nearest hazard (m)")
plt.plot(x_km, y_km, "r*", markersize=15)
plt.title("Site01: best landing spot")
plt.show()