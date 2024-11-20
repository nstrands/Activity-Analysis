import csv
from shapely.geometry import LineString, Point
import geopandas as gpd
from pyproj import Transformer

class ActivityHandler:
    def __init__(self):
        pass

    def build_path(self, points):
        # Build a LineString using points (longitude, latitude pairs)
        line = LineString(points)
        print(f"Number of points used to create the geometry: {len(points)}")
        return line

    def calculate_stats(self, line, start_time, end_time):
        # Project LineString to calculate distance in meters, then convert to miles
        transformer = Transformer.from_crs("epsg:4326", "epsg:32617", always_xy=True)
        projected_line = LineString([transformer.transform(x, y) for x, y in line.coords])
        distance_meters = projected_line.length
        distance_miles = distance_meters * 0.000621371  # Convert meters to miles

        # Calculate trip duration in minutes
        start_minutes, start_seconds = map(float, start_time.split(":"))
        end_minutes, end_seconds = map(float, end_time.split(":"))
        duration_minutes = (end_minutes + end_seconds / 60) - (start_minutes + start_seconds / 60)

        # Calculate average speed (miles per hour) and average pace (minutes per mile)
        avg_speed = distance_miles / (duration_minutes / 60)
        avg_pace = duration_minutes / distance_miles

        # Create a dictionary with the stats
        stats = {
            "distance_miles": distance_miles,
            "average_speed_mph": avg_speed,
            "average_pace_min_per_mile": avg_pace
        }

        # Print the statistics
        print(f"Distance covered: {distance_miles:.2f} mi")
        print(f"Average speed: {avg_speed:.2f} mi/h")
        print(f"Average pace: {avg_pace:.2f} min/mi")

        return stats

    def get_centroid(self, geometry):
        # Get the centroid of a geometry object
        centroid = geometry.centroid
        print(f"Centroid coordinates: ({centroid.x}, {centroid.y})")
        return centroid

    def export_activity(self, path, stats):
        # Create a GeoDataFrame from the LineString
        line_geoseries = gpd.GeoSeries([path], crs="epsg:4326")
        gdf = gpd.GeoDataFrame({
            "geometry": line_geoseries,
            "distance_miles": [stats["distance_miles"]],
            "average_speed_mph": [stats["average_speed_mph"]],
            "average_pace_min_per_mile": [stats["average_pace_min_per_mile"]]
        })

        # Save the GeoDataFrame as an ESRI Shapefile
        gdf.to_file("activity_output.shp", driver="ESRI Shapefile")

if __name__ == '__main__':
    # Create lists to store coordinate pairs and timestamps
    coordinate_list = []
    timestamps = []

    # Open CSV file to iterate through rows to extract longitude, latitude, and time
    csv_file_path = r"C:\Users\nstra\iCloudDrive\Desktop\School\GIS6103 GIS Programming and Customization\Assignments\Assignment-11\gps_track.csv"
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])
            coordinate_list.append((longitude, latitude))
            timestamps.append(row['time'])

    # Create an instance of ActivityHandler
    activity_handler = ActivityHandler()

    # Build a shapely LineString
    path = activity_handler.build_path(coordinate_list)

    # Calculate trip statistics
    start_time = timestamps[0]
    end_time = timestamps[-1]
    stats = activity_handler.calculate_stats(path, start_time, end_time)

    # Get the centroid of the trip
    centroid = activity_handler.get_centroid(path)

    # Export activity as a Shapefile
    activity_handler.export_activity(path, stats)