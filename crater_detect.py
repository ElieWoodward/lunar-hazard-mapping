import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, label, find_objects
from projection import latlon_to_xy

# ---- Settings ----
ELEVATION_FILE = "data/Site01_final_adj_5mpp_surf.tif"
PIXEL_M = 5
BLUR_SIGMA_PX = 100        # 100 px x 5 m = 500 m blur
DEPTH_THRESHOLD_M = -10    # how far below surroundings counts as a dip
BORDER_PX = 200            # 200 px x 5 m = 1 km ignored at each edge
MIN_DIAMETER_M = 20        # smaller than this is likely noise
MIN_ASPECT = 0.7           # 1.0 = perfectly round bounding box
FILL_MIN = 0.6             # a perfect circle fills pi/4 = 0.785
FILL_MAX = 0.9
SLOPE_FILE = "data/Site01_final_adj_5mpp_slp.tif"


# ---- Functions ----
def load_map(path):
    """Load a single-band GeoTIFF as a NumPy array."""
    with rasterio.open(path) as src:
        return src.read(1)


def local_relief(elevation, sigma_px):
    """Elevation minus a blurred copy, leaving only small-scale bumps and dips."""
    return elevation - gaussian_filter(elevation, sigma=sigma_px)


def mask_border(mask, border_px):
    """Return a copy with a border of the given width set to False."""
    result = mask.copy()
    result[:border_px, :] = False
    result[-border_px:, :] = False
    result[:, :border_px] = False
    result[:, -border_px:] = False
    return result

def measure_blobs(labeled, pixel_m):
    """Position, size, and shape of every labeled blob."""
    results = []
    for i, box in enumerate(find_objects(labeled)):
        blob = labeled[box] == i + 1
        area_px = blob.sum()
        h = box[0].stop - box[0].start
        w = box[1].stop - box[1].start
        results.append({
            "row": (box[0].start + box[0].stop) / 2,
            "col": (box[1].start + box[1].stop) / 2,
            "diameter_m": 2 * np.sqrt(area_px / np.pi) * pixel_m,
            "aspect": min(h, w) / max(h, w),
            "fill": area_px / (h * w),
            "row_min": box[0].start,
            "row_max": box[0].stop,
            "col_min": box[1].start,
            "col_max": box[1].stop,
        })
    return pd.DataFrame(results)

# ---- Main ----
elevation = load_map(ELEVATION_FILE)
rows, cols = elevation.shape
relief = local_relief(elevation, BLUR_SIGMA_PX)
candidates = mask_border(relief < DEPTH_THRESHOLD_M, BORDER_PX)

labeled, n = label(candidates)
print(n, "candidate depressions")

blobs = measure_blobs(labeled, PIXEL_M)

touches_border = (
    (blobs["row_min"] <= BORDER_PX)
    | (blobs["row_max"] >= rows - BORDER_PX)
    | (blobs["col_min"] <= BORDER_PX)
    | (blobs["col_max"] >= cols - BORDER_PX)
)
size_ok = blobs["diameter_m"] >= MIN_DIAMETER_M
round_ok = (
    (blobs["aspect"] >= MIN_ASPECT)
    & (blobs["fill"] >= FILL_MIN)
    & (blobs["fill"] <= FILL_MAX)
)

detected = blobs[size_ok & round_ok & ~touches_border]
print(len(detected), "crater detections")
detected.to_csv("detected_craters.csv", index=False)

extent = [0, cols * PIXEL_M / 1000, rows * PIXEL_M / 1000, 0]

fig, axes = plt.subplots(1, 2)
axes[0].imshow(relief, cmap="RdBu", vmin=-50, vmax=50, extent=extent)
axes[0].set_title("Local relief")
axes[1].imshow(labeled > 0, cmap="gray", extent=extent)
axes[1].set_title("Candidates")
plt.show()

# ---- Settings ----
ELEVATION_FILE = "data/Site01_final_adj_5mpp_surf.tif"
PIXEL_M = 5
BLUR_SIGMA_PX = 100        # 100 px x 5 m = 500 m blur
DEPTH_THRESHOLD_M = -10    # how far below surroundings counts as a dip
BORDER_PX = 200            # 200 px x 5 m = 1 km ignored at each edge


# ---- Functions ----
def load_map(path):
    """Load a single-band GeoTIFF as a NumPy array."""
    with rasterio.open(path) as src:
        return src.read(1)


def local_relief(elevation, sigma_px):
    """Elevation minus a blurred copy, leaving only small-scale bumps and dips."""
    return elevation - gaussian_filter(elevation, sigma=sigma_px)


def mask_border(mask, border_px):
    """Return a copy with a border of the given width set to False."""
    result = mask.copy()
    result[:border_px, :] = False
    result[-border_px:, :] = False
    result[:, :border_px] = False
    result[:, -border_px:] = False
    return result


# ---- Main ----
elevation = load_map(ELEVATION_FILE)
rows, cols = elevation.shape
extent = [0, cols * PIXEL_M / 1000, rows * PIXEL_M / 1000, 0]

relief = local_relief(elevation, BLUR_SIGMA_PX)
candidates = mask_border(relief < DEPTH_THRESHOLD_M, BORDER_PX)

labeled, n = label(candidates)
print(n, "candidate depressions")

blobs = measure_blobs(labeled, PIXEL_M)

touches_border = (
    (blobs["row_min"] <= BORDER_PX)
    | (blobs["row_max"] >= rows - BORDER_PX)
    | (blobs["col_min"] <= BORDER_PX)
    | (blobs["col_max"] >= cols - BORDER_PX)
)
size_ok = blobs["diameter_m"] >= MIN_DIAMETER_M
round_ok = (
    (blobs["aspect"] >= MIN_ASPECT)
    & (blobs["fill"] >= FILL_MIN)
    & (blobs["fill"] <= FILL_MAX)
)

detected = blobs[size_ok & round_ok & ~touches_border]
print(len(detected), "crater detections")
detected.to_csv("detected_craters.csv", index=False)

slope = load_map(SLOPE_FILE)

catalog = pd.read_csv("data/lunar_crater_database_robbins_2018.csv")
south = catalog[catalog["LAT_CIRC_IMG"] < -88]
x, y = latlon_to_xy(south["LAT_CIRC_IMG"], south["LON_CIRC_IMG"])
inside = (x >= -19000) & (x <= -3000) & (y >= -20000) & (y <= -4000)

plt.imshow(slope, cmap="gray", vmax=30, extent=extent)

for _, crater in detected.iterrows():
    cx = crater["col"] * PIXEL_M / 1000
    cy = crater["row"] * PIXEL_M / 1000
    r = crater["diameter_m"] / 2 / 1000
    plt.gca().add_patch(plt.Circle((cx, cy), r, fill=False, color="cyan"))

for cx, cy, d in zip((x[inside] + 19000) / 1000,
                     (-4000 - y[inside]) / 1000,
                     south["DIAM_CIRC_IMG"][inside]):
    plt.gca().add_patch(plt.Circle((cx, cy), d / 2, fill=False, color="red"))

plt.title("Detected (cyan) vs catalog (red)")
plt.show()