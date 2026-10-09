import pandas as pd
from projection import latlon_to_xy

craters = pd.read_csv("data/lunar_crater_database_robbins_2018.csv")
south = craters[craters["LAT_CIRC_IMG"] < -88]

x, y = latlon_to_xy(south["LAT_CIRC_IMG"], south["LON_CIRC_IMG"])

inside = (x >= -19000) & (x <= -3000) & (y >= -20000) & (y <= -4000)
site_craters = south[inside]

print(len(site_craters), "craters inside Site01")
print(site_craters[["LAT_CIRC_IMG", "LON_CIRC_IMG", "DIAM_CIRC_IMG"]])