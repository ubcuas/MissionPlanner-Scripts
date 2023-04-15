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
    longitude - longitude to conver, in degrees

    Implements conversion from GPS coordinates (latitude and longitude) to UTM
    coordinates (easting and northing).

    For simplicity, assumes operation west of the prime meridian, below the
    arctic circle, andabove the antarctic circle (most of the western
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

def convert_gps_to_utm_online(latitude, longitude):
    """
    Parameters:
    latitude - latitude to convert, in degrees
    longitude - longitude to conver, in degrees

    Implements conversion from GPS coordinates (latitude and longitude) to UTM
    coordinates (easting and northing).

    This is done by making a request to a conversion website, www.latlong.net,
    and extracting the converted UTM coordinates from the response.
    This decision was made for ease of implementation, as it avoids the need
    to directly code the complex conversion formulas between the two coordinate
    systems. Consequently, however, this does mean that the program must have
    access to the internet in order to function.
    This function is also rate-limited to one call per second.
    """
    # Create target URL
    conversion_url = "https://www.latlong.net" + f"/c/?lat={latitude}&long={longitude}"

    # Make a request to the conversion site
    response = requests.get(conversion_url, timeout=1)

    # Extract the portion of the HTML containing the UTM coordinates
    response = (response.text.split("UTM Zone")[-1]).split("</table>")[0]
    utm_e, utm_n = response.split("<td>")[1:3]

    # Remove HTML tags, whitespace, and commas, convert to float
    utm_e = float(utm_e.split("</td>")[0].strip().replace(",", ""))
    utm_n = float(utm_n.split("</td>")[0].strip().replace(",", ""))

    return (utm_e, utm_n)

def distance_utm(coords1, coords2):
    """
    Computes the distance (in meters) between the two input UTM coordinate sets.
    """
    return sqrt(pow(coords2[0] - coords1[0], 2) + pow(coords2[1] - coords1[1], 2))

