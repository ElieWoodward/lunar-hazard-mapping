import rasterio
import matplotlib.pyplot as plt

with rasterio.open("data/Site01_final_adj_5mpp_surf.tif") as src:
    z = src.read(1)
    print(z.shape)
    print(src.res)
    print(z.min(), z.max())

safe = z < 10
print(safe[0, 0])
print(safe.mean() * 100, "% of the area is under 10 degrees")

plt.imshow(z, cmap="terrain")
plt.colorbar(label="Elevation (m)")
plt.title("Site01: Connecting Ridge, lunar south pole")
plt.show()
