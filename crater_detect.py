import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, label, find_objects
from projection import latlon_to_xy

# ---- Settings ----
ELEVATION_FILE = "data/Site01_final_adj_5mpp_surf.tif"
SLOPE_FILE = "data/Site01_final_adj_5mpp_slp.tif"
CATALOG_FILE = "data/lunar_crater_database_robbins_2018.csv"

PIXEL_M = 5
MAP_LEFT_M = -19000        # map edges in projection meters (from site_info.py)
MAP_RIGHT_M = -3000
MAP_TOP_M = -4000
MAP_BOTTOM_M = -20000

BLUR_SIGMA_PX = 100        # 100 px x 5 m = 500 m blur
DEPTH_THRESHOLD_M = -10    # threshold used for the final map and CSV
SWEEP_THRESHOLDS_M = [-5, -10, -15, -20]
BORDER_PX = 200            # 200 px x 5 m = 1 km ignored at each edge
MIN_DIAMETER_M = 20        # smaller than this is likely noise
MIN_ASPECT = 0.7           # 1.0 = perfectly round bounding box
FILL_MIN = 0.6             # a perfect circle fills pi/4 = 0.785
FILL_MAX = 0.9


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


def filter_craters(blobs, rows, cols):
    """Keep blobs that are big enough, round, and not cut off by the border."""
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
    return blobs[size_ok & round_ok & ~touches_border]


def detect_craters(relief, threshold_m, rows, cols):
    """Run the full detector at one depth threshold. Returns detections and candidate count."""
    candidates = mask_border(relief < threshold_m, BORDER_PX)
    labeled, n = label(candidates)
    blobs = measure_blobs(labeled, PIXEL_M)
    if len(blobs) == 0:
        return blobs, n
    return filter_craters(blobs, rows, cols), n


def load_site_catalog():
    """Catalog craters inside Site01, as x/y/diameter in km from the top-left corner."""
    catalog = pd.read_csv(CATALOG_FILE)
    south = catalog[catalog["LAT_CIRC_IMG"] < -88]
    x, y = latlon_to_xy(south["LAT_CIRC_IMG"].to_numpy(),
                        south["LON_CIRC_IMG"].to_numpy())
    d = south["DIAM_CIRC_IMG"].to_numpy()
    inside = ((x >= MAP_LEFT_M) & (x <= MAP_RIGHT_M)
              & (y >= MAP_BOTTOM_M) & (y <= MAP_TOP_M))
    x_km = (x[inside] - MAP_LEFT_M) / 1000
    y_km = (MAP_TOP_M - y[inside]) / 1000
    return x_km, y_km, d[inside]


def match_to_catalog(det_x, det_y, det_d, cat_x, cat_y, cat_d):
    """For each catalog crater, True if a detection matches its position and size."""
    found = []
    for cx, cy, d in zip(cat_x, cat_y, cat_d):
        dist = np.sqrt((det_x - cx)**2 + (det_y - cy)**2)
        close = dist <= d / 4
        similar = (det_d >= d / 2) & (det_d <= d * 2)
        found.append((close & similar).any())
    return np.array(found)


def evaluate(detected, cat_x, cat_y, cat_d):
    """Which catalog craters the detections found (True/False for each)."""
    if len(detected) == 0:
        return np.zeros(len(cat_x), dtype=bool)
    det_x = detected["col"].to_numpy() * PIXEL_M / 1000
    det_y = detected["row"].to_numpy() * PIXEL_M / 1000
    det_d = detected["diameter_m"].to_numpy() / 1000
    return match_to_catalog(det_x, det_y, det_d, cat_x, cat_y, cat_d)


# ---- Main: setup ----
elevation = load_map(ELEVATION_FILE)
rows, cols = elevation.shape
map_w_km = cols * PIXEL_M / 1000
map_h_km = rows * PIXEL_M / 1000
extent = [0, map_w_km, map_h_km, 0]

relief = local_relief(elevation, BLUR_SIGMA_PX)

cat_x, cat_y, cat_d = load_site_catalog()
border_km = BORDER_PX * PIXEL_M / 1000
fair = ((cat_x >= border_km) & (cat_x <= map_w_km - border_km)
        & (cat_y >= border_km) & (cat_y <= map_h_km - border_km))
cat_x, cat_y, cat_d = cat_x[fair], cat_y[fair], cat_d[fair]
print(len(cat_d), "catalog craters in the evaluated area")

# ---- Main: sweep ----
print("Threshold (m) | Candidates | Detections | Recall (%)")
for t in SWEEP_THRESHOLDS_M:
    det, n = detect_craters(relief, t, rows, cols)
    found = evaluate(det, cat_x, cat_y, cat_d)
    print(t, "|", n, "|", len(det), "|", round(found.mean() * 100, 1))

# ---- Main: final run at the chosen threshold ----
detected, n = detect_craters(relief, DEPTH_THRESHOLD_M, rows, cols)
detected.to_csv("detected_craters.csv", index=False)
found = evaluate(detected, cat_x, cat_y, cat_d)
print("Final threshold", DEPTH_THRESHOLD_M, "m:", len(detected), "detections,",
      round(found.mean() * 100, 1), "% recall")
for d, f in sorted(zip(cat_d, found)):
    print(f"  {d:.2f} km  {'found' if f else 'missed'}")
det_x = detected["col"].to_numpy() * PIXEL_M / 1000
det_y = detected["row"].to_numpy() * PIXEL_M / 1000
det_d = detected["diameter_m"].to_numpy() / 1000
det_r = det_d / 2

print("Why each missed crater was missed:")
for cx, cy, d, f in zip(cat_x, cat_y, cat_d, found):
    if not f:
        dist = np.sqrt((det_x - cx)**2 + (det_y - cy)**2)
        i = dist.argmin()
        print(f"  {d:.2f} km: nearest detection {dist[i]:.2f} km away, "
              f"{det_d[i]:.2f} km wide")

# ---- Main: plot ----
slope = load_map(SLOPE_FILE)
plt.imshow(slope, cmap="gray", vmax=30, extent=extent)
for cx, cy, r in zip(det_x, det_y, det_r):
    plt.gca().add_patch(plt.Circle((cx, cy), r, fill=False, color="cyan"))
for cx, cy, d in zip(cat_x, cat_y, cat_d):
    plt.gca().add_patch(plt.Circle((cx, cy), d / 2, fill=False, color="red"))
plt.title("Detected (cyan) vs catalog (red)")
plt.show()