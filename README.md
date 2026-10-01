# lunar-hazard-mapping

Finds safe landing sites at the lunar south pole using NASA elevation data.

![Best landing spot:Zone 01](figures/figures/Site 01 - Best Landing Spot.png)

## What it does:
Landers, such as those SpaceX is building(Starships), need a large flat area, under 10 degrees, to land on. What the code I've written so far does, is it calculates the slope of the surrounding ground, finds where a landing zone fits, based on pixels being dubbed as "safe" or "unsafe", and then picks a pixel that is the furthest from all hazards, or "unsafe" pixels, making it the largest "safe" landing area on the map. 

## How it works:
The code works by first grabbing the elevation from a NASA .tif file and computing the slope using central differences. It marks all computed slopes under 10 degrees as safe pixels, doing it with all surrounding it, then uses erosion to detect different safe regions depending on radius, the uses the "safe" and "unsafe" computed pixels and distance transform to find the pixel furthest from any unsafe pixels, and marks it as the best landing zone. 

## Results

### Study area
Site01 (Connecting Ridge) covers 16 km × 16 km near Shackleton crater
(3200 × 3200 pixels at 5 m per pixel). Elevation ranges from −523.2 m
to 1959.5 m, a span of about 2.5 km.

### Slope validation
I computed slope from the elevation map using central differences and compared it to NASA's published slope map pixel by pixel. The average difference is 0.00067°. Excluding the one-pixel border, the largest difference is 0.011°. On the border the largest difference is 25.9°, because central differences need a neighbor on both sides and edge pixels only have one. The code treats edge pixels as unsafe for this reason.

### Landable area by zone size
A pixel counts as landable when every pixel within a circular landing
zone around it has a slope under 10°.

Under 10° slope (single pixel): 36.37% of the site.

| Zone width | Landable area |
|---|---|
| 20 m | 25.20% |
| 50 m | 14.11% |
| 100 m | 5.94% |
| 200 m | 1.11% |
| 400 m | 0.02% |

Landable area shrinks faster as the zone grows. About 42% of the landable area survives going from 50 m to 100 m, 19% from 100 m to 200 m, and only 2% from 200 m to 400 m. The largest flat patches at this site are a few hundred meters across.

### Best landing site
Using slope alone, the safest point is 10.085 km across and 2.940 km down from the top-left corner of the tile, in the upper flat region of the map. The nearest slope steeper than 10° is about 267 m away.

![Best landing spot:Zone 01](figures/figures/Site 01 - Best Landing Spot.png)

## Limitations
There are a few key things this program can't do yet, which it hopefully will be able to soon, it misses boulders at 5m resolutions and small craters, which will be fixed by a crater detection system. There isn't any sunlight or Earth line-of-sight analysis, and edges are also excluded. All of those should be addressed by the final product

## Data
Elevation and slope maps come from NASA Goddard's Planetary Geodesy
Data Archive (PGDA), "South Pole Landing Site LOLA DEMs":
https://pgda.gsfc.nasa.gov/products/78

Files used (Site01: Connecting ridge):
- `Site01_final_adj_5mpp_surf.tif` - surface elevation (m)
- `Site01_final_adj_5mpp_slp.tif` - slope (degrees), used to validate my slope calculation

Both are 5 m/pixel GeoTIFFs in south polar stereographic coordinates, derived from Lunar Orbiter Laser Altimeter (LOLA) data aboard NASA's Lunar Reconnaissance Orbiter.

Citation:
Barker, M. K., et al. (2021). Improved LOLA elevation maps for south pole landing sites: Error estimates and their impact on illumination conditions. Planetary and Space Science, 203, 105119. https://doi.org/10.1016/j.pss.2020.105119

## How to run
1. Install Python 3 and the required packages:
```
   python -m pip install -r requirements.txt
```
2. Download the two Site01 files listed under Data and place them in
   a `data/` folder in the project root.
3. Run:
```
   python find_landing_site.py
```
   This prints the safe-area percentages and the best landing site, and opens a map of distance to the nearest hazard.

## Use of AI
I am using lots of AI for this project, Claude mainly. I am a very interested person, who wants to know all about this subject, and yet currently has very little knowledge. I am a fast and capable learner, and am at the very least taking notes on and understanding the code Claude writes for me as we go through the development process. I go through it line by line, with Claude's explanation if necessary, fully understanding what each line does, and why it's there.