import pandas as pd
import rasterio
import matplotlib.pyplot as plt
from projection import latlon_to_xy

with rasterio.open("data/Site01_final_adj_5mpp_surf.tif") as src:
    z = src.read(1)

craters = pd.read_csv("data/lunar_crater_database_robbins_2018.csv")
south = craters[craters["LAT_CIRC_IMG"] < -88]
x, y = latlon_to_xy(south["LAT_CIRC_IMG"], south["LON_CIRC_IMG"])
inside = (x >= -19000) & (x <= -3000) & (y >= -20000) & (y <= -4000)

cx_km = (x[inside] + 19000) / 1000
cy_km = (-4000 - y[inside]) / 1000
r_km = south["DIAM_CIRC_IMG"][inside] / 2

with rasterio.open("data/Site01_final_adj_5mpp_slp.tif") as src:
    slope = src.read(1)

plt.imshow(slope, cmap="gray", vmax=30, extent=[0, 16, 16, 0])
for cx, cy, r in zip(cx_km, cy_km, r_km):
    circle = plt.Circle((cx, cy), r, fill=False, color="red")
    plt.gca().add_patch(circle)
plt.title("Site01 with catalog craters")
plt.show()