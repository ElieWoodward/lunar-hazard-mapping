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

### Crater detection (classical baseline)
The detector finds craters as local depressions in the elevation map.
It subtracts a blurred copy of the map (500 m Gaussian blur) to remove
large-scale terrain, marks pixels more than 10 m below their
surroundings, groups touching pixels into blobs, and keeps blobs that
are at least 20 m across, round, and not cut off by the 1 km border.
This turned 555 candidate depressions into 108 detections.

I evaluated it against the 18 Robbins catalog craters inside the
evaluated area. A catalog crater counts as found only if a detection's
center is within a quarter of its diameter and the detection is between
half and double its size. An earlier, looser rule (any detection inside
the crater) gave 77.8% recall, but a density check showed large craters
were getting credit for unrelated small detections by chance.

Recall: 27.8% (5 of 18). By size, the detector found 4 of 6 craters
2 km or smaller and 1 of 12 craters larger than 2 km.

| Depth threshold | Candidates | Detections | Recall |
|---|---|---|---|
| -5 m | 590 | 125 | 22.2% |
| -10 m | 555 | 108 | 27.8% |
| -15 m | 530 | 110 | 27.8% |
| -20 m | 402 | 88 | 22.2% |

Changing the threshold moved recall by one crater, so the threshold is
not the limiting factor. For 9 of the 13 missed craters, no detection
was anywhere near the center. For the other 4, the only nearby
detections were small craters 30 to 100 m wide sitting inside the larger
crater. The method does not detect craters wider than about 2 km,
especially old, degraded ones. Many detections are sub-kilometer
craters that the catalog does not include, so precision can't be
measured against the catalog and needs hand-labeled data.

![Detected vs catalog craters](figures/"Site 01 - Detected (cyan) vs Catalog (red)")

## Limitations
There are a few key things this program can't do yet, which it hopefully will be able to soon, it misses boulders at 5m resolutions and small craters, which will be fixed by a crater detection system. There isn't any sunlight or Earth line-of-sight analysis, and edges are also excluded. All of those should be addressed by the final product

## Data
Elevation and slope maps come from NASA Goddard's Planetary Geodesy
Data Archive (PGDA), "South Pole Landing Site LOLA DEMs":
https://pgda.gsfc.nasa.gov/products/78
Crater catalog: Robbins Lunar Crater Database (USGS Astrogeology),

Files used (Site01: Connecting ridge):
- `Site01_final_adj_5mpp_surf.tif` - surface elevation (m)
- `Site01_final_adj_5mpp_slp.tif` - slope (degrees), used to validate my slope calculation
- `lunar_crater_database_robbins_2018.csv`

Both .tif's are 5 m/pixel GeoTIFFs in south polar stereographic coordinates, derived from Lunar Orbiter Laser Altimeter (LOLA) data aboard NASA's Lunar Reconnaissance Orbiter.

Citation:
Barker, M. K., et al. (2021). Improved LOLA elevation maps for south pole landing sites: Error estimates and their impact on illumination conditions. Planetary and Space Science, 203, 105119. https://doi.org/10.1016/j.pss.2020.105119
Robbins, S. J. (2019). A new global database of lunar impact craters
>1–2 km: 1. Crater locations and sizes, comparisons with published
databases, and global analysis. Journal of Geophysical Research:
Planets, 124, 871–892. https://doi.org/10.1029/2018JE005592

## How to run
1. Install Python 3 and the required packages:
```
   python -m pip install -r requirements.txt
```
2. Download the files listed under Data and place them in
   a `data/` folder in the project root.
3. Run:
```
   python find_landing_site.py
```
   This prints the safe-area percentages and the best landing site, and opens a map of distance to the nearest hazard.
4. Run the crater detector:
   This prints a threshold sweep, recall against the catalog, and the
   reason for each missed crater, saves `detected_craters.csv`, and shows
   detections over the slope map.
## Roadmap
- Machine learning crater detector (U-Net), trained on NASA's 20 m/px
  south pole map with the Robbins catalog as labels, and compared
  against the classical baseline
- Combined hazard map using both slope and detected craters
- Report the landing site in lunar latitude and longitude instead of
  tile coordinates
- Powered descent simulation from lunar orbit to the selected site
- Script to download the required data automatically
## Use of AI
I am using lots of AI for this project, Claude mainly. I am a very interested person, who wants to know all about this subject, and yet currently has very little knowledge. I am a fast and capable learner, and am at the very least taking notes on and understanding the code Claude writes for me as we go through the development process. I go through it line by line, with Claude's explanation if necessary, fully understanding what each line does, and why it's there. I am also doing most of the mathematical calculations by hand, even though Claude just could, because I'm in Calculus II, and want to use what I've learned.