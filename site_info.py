import rasterio

with rasterio.open("data/Site01_final_adj_5mpp_surf.tif") as src:
    print(src.crs)
    print(src.bounds)
    print(src.transform)