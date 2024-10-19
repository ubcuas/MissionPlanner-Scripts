"""
Provides functionality for working with UTM coordinates. This includes
conversion from GPS coordinates (latitude andlongitude) and calculating
distance between two UTM coordiantes.
"""

from math import *

def convert_gps_to_utm(latitude, longitude):
    """
    Parameters:
    latitude - latitude to convert, in degrees
    longitude - longitude to convert, in degrees

    Implements conversion from GPS coordinates (latitude and longitude) to UTM
    coordinates (easting and northing).

    For simplicity, assumes operation west of the prime meridian, below the
    arctic circle, and above the antarctic circle (most of the western
    hemisphere.)
    """
    # Convert to radians
    rad_lat = radians(latitude)
    rad_lon = radians(longitude)

    # Get reference meridian
    lon_ref = ((longitude + 180) // 6) * 6 - 180 + 3
    rad_lon_ref = radians(lon_ref)

    # Calculation constants
    A_RAD = 6378.137
    F = 1 / 298.257223563
    N0 = 0 if latitude >= 0 else 10000
    E0 = 500
    K0 = 0.9996

    # Preliminary values
    N = F / (2 - F)
    A = A_RAD / (1 + N) *(1 + pow(N, 2) / 4 + pow(N, 4) / 64)
    ALPHA = [0, N / 2 - 2 / 3 * pow(N, 2) + 15 / 16 * pow(N, 3),
                13 / 48 * pow(N, 2) - 3 / 5 * pow(N, 3),
                61 / 240 * pow(N, 3)]

    # Intermediate values
    n_prime = 2 * sqrt(N) / (1 + N)
    t = sinh(atanh(sin(rad_lat)) - n_prime * atanh(n_prime * sin(rad_lat)))
    xi_prime = atan(t / cos(rad_lon - rad_lon_ref))
    eta_prime = atanh(sin(rad_lon - rad_lon_ref) / sqrt(1 + t * t))

    # Final calculations
    utm_e_km = E0 + K0 * A * (eta_prime + sum(ALPHA[j] * cos(2 * j * xi_prime) * sinh(2 * j * eta_prime) for j in range(1, 4)))
    utm_n_km = N0 + K0 * A * (xi_prime + sum(ALPHA[j] * sin(2 * j * xi_prime) * cosh(2 * j * eta_prime) for j in range(1, 4)))

    return (utm_e_km * 1000, utm_n_km * 1000)

def convert_gps_to_utm_zone(longitude):
    return ((longitude + 180) // 6) % 60 + 1

def convert_utm_to_gps(easting, northing, zone, hemisphere):
    """
    easting - meters East
    northing - meters North
    zone - UTM zone
    hemisphere - +1 for north, -1 for south

    returns (latitude, longitude) in degrees
    """

    #calculation constants
    A_RAD = 6378.137
    F = 1 / 298.257223563
    N0 = 0 if hemisphere >= 0 else 10000
    E0 = 500
    K0 = 0.9996

    #preliminary values
    N = F / (2 - F)
    A = A_RAD / (1 + N) *(1 + pow(N, 2) / 4 + pow(N, 4) / 64)
    BETA = [0, N / 2 - 2 / 3 * pow(N, 2) + 37 / 96 * pow(N, 3),
                1 / 48 * pow(N, 2) + 1 / 15 * pow(N, 3),
                17 / 480 * pow(N, 3)]
    DELTA = [0, 2 * N - 2 / 3 * pow(N, 2) - 2 * pow(N, 3),
                7 / 3 * pow(N, 2) - 8 / 5 * pow(N, 3),
                56 / 15 * pow(N, 3)]
    
    #intermediate values
    xi = (northing / 1000 - N0) / (K0 * A)
    eta = (easting / 1000 - E0) / (K0 * A)

    xi_prime = xi - sum([BETA[j] * sin(2 * j * xi) * cosh(2 * j * eta) for j in range(1, 4)])
    eta_prime = eta - sum([BETA[j] * cos(2 * j * xi) * sinh(2 * j * eta) for j in range(1, 4)])
    chi = asin(sin(xi_prime) / cosh(eta_prime))

    #final calulations
    rad_lat = chi + sum([DELTA[j] * sin(2 * j * chi) for j in range(1, 4)])
    rad_lng = radians(zone * 6 - 183) + atan(sinh(eta_prime) / cos(xi_prime))
    #grid_convergence = hemisphere * atan((tau_prime + sigma_prime * tan(xi_prime) * tanh(eta_prime)) / (sigma_prime - tau_prime * tan(xi_prime) * tanh(eta_prime)))

    latitude = rad_lat * (180 / pi)
    longitude = rad_lng * (180 / pi)

    return (latitude, longitude)

def distance_utm(coords1, coords2):
    """
    Computes the distance (in meters) between the two input UTM coordinate sets.
    """
    return sqrt(pow(coords2[0] - coords1[0], 2) + pow(coords2[1] - coords1[1], 2))

if __name__ == "__main__":
    test = (38.1491375, -76.5644073)
    utm = convert_gps_to_utm(test[0], test[1])
    zone = convert_gps_to_utm_zone(test[1])
    back = convert_utm_to_gps(utm[0], utm[1], zone, 1)

    print(f"TEST VALUES {test}\nUTM {utm} ZONE {zone}\nGPS BACK {back}")