import numpy as np

R=1737400

def latlon_to_xy(lat, lon):
    psi = 90 + lat
    psi_rad = np.radians(psi)
    rho = 2 * R * np.sin(psi_rad / 2)
    lon_rad = np.radians(lon)
    x = rho * np.sin(lon_rad)
    y = rho * np.cos(lon_rad)
    return x, y

if __name__ == "__main__":
    print(latlon_to_xy(-90, 0))
    print(latlon_to_xy(-89, 0))
    print(latlon_to_xy(-89, 90))