import math
import random


def add_noise_to_gps_coordinates(
    lat: float, lon: float, min_radius: float, max_radius: float
) -> tuple[float, float]:
    """
    Generate a random point between min_radius and max_radius (meters)
    around the original coordinate.
    Returns ("0", "0") if an error occurs.
    """
    try:
        earth_radius = 6378137  # meters

        # Convert lat/lon to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        # Uniform distribution in area (important!)
        distance = math.sqrt(random.uniform(min_radius**2, max_radius**2))

        # Angular distance
        angular_distance = distance / earth_radius

        # Random bearing
        bearing = random.uniform(0, 2 * math.pi)

        # Destination point formula
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance)
            + math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing)
        )

        new_lon_rad = lon_rad + math.atan2(
            math.sin(bearing) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad),
        )

        return math.degrees(new_lat_rad), math.degrees(new_lon_rad)

    except (TypeError, ValueError, AttributeError):
        return 0.0, 0.0
