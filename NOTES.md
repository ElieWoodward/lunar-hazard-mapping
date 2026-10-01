# lunar hazard mapping notes

Python Notes:
def creates a function, you use def "function name"("parameter name"), return at the end of the indent sets you return value

with lets you open a file, using with (rasterio.open if using) as "short name, ex: src"

All caps, Ex: ELEVATION_FILE =, makes it so that value won't change throughout program

scipy, use binary_erosion, only keeps pixels on a map that meet certain criteria, such as 3x3 needs to be safe etc. also use distance_transform_edt, measures straight line distance to nearest "unsafe pixel", spot near unsafe gets low number, further from unsafe gets higher number, highest number gives safest landing spot.

