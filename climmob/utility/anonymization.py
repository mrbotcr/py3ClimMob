import math
import random


def add_noise_to_gps_coordinates(lat, lon, radius):
    """
    Add noise to a geographical coordinate by choosing a random point within a radius.

    Parameters:
    lat (float): Latitude of the original coordinate.
    lon (float): Longitude of the original coordinate.
    radius (float): Radius in meters within which to choose a random point.

    Returns:
    tuple: A tuple containing the new latitude and longitude.
    """
    try:
        # Earth radius in meters
        earth_radius = 6378137

        # Convert radius from meters to degrees latitude
        radius_lat = radius / (earth_radius * (math.pi / 180))

        # Convert radius from meters to degrees longitude, adjusted by latitude
        radius_lon = radius / (
            earth_radius * (math.pi / 180) * math.cos(math.radians(lat))
        )

        # Random angle in radians
        angle = random.uniform(0, 2 * math.pi)

        # Random distance factor for uniform distribution in a circle
        factor = math.sqrt(random.uniform(0, 1))

        # Calculate deltas
        delta_lat = factor * radius_lat * math.cos(angle)
        delta_lon = factor * radius_lon * math.sin(angle)

        # New latitude and longitude
        new_lat = lat + delta_lat
        new_lon = lon + delta_lon

        return str(new_lat), str(new_lon)
    except Exception as e:
        print(e)
        return "Error", "Error"
