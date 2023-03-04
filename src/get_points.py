import geopandas as gpd
import json as json
import pandas as pd
import math
from shapely.geometry import shape, LineString
from shapely.ops import split
import re


def split_shapes(geometry):
    geometry_wkt = geometry.wkt
    pattern = r"(-?\d+\.\d+)\s+(-?\d+\.\d+)"
    matches = re.findall(pattern, geometry_wkt)
    x_values = [float(match[0]) for match in matches]
    y_values = [float(match[1]) for match in matches]
    x_length = max(x_values) - min(x_values)
    y_length = max(y_values) - min(y_values)
    centroid = geometry.centroid
    centroid_x, centroid_y = centroid.x, centroid.y
    if x_length>y_length:
        # Split shape with vertical line
        line = LineString([(centroid_x, centroid_y+y_length), (centroid_x, centroid_y-y_length)])
    else:
        # Split shape with horizontal line
        line = LineString([(centroid_x+x_length, centroid_y), (centroid_x-x_length, centroid_y)])
    result = split(geometry, line)
    # half1, half2 = result[0], result[1]
    return result


df_parishes = pd.read_csv('../data/parishes.csv')
with open('../data/parish_shapefile_merged.json', 'r') as f:
    shapes = json.load(f)

df_parishes_filtered = df_parishes[df_parishes['include'] == True]
parishes = [x for x in df_parishes_filtered['parish']]
municipalities = df_parishes_filtered['municipality'].unique()
points = []
parishes_df = []
point_names_df = []
for feature in shapes['features']:
    shape_geometry = feature['geometry']
    geometry = shape(shape_geometry)
    halves = split_shapes(geometry)
    slices1 = split_shapes(halves[0])
    slices2 = split_shapes(halves[1])
    new_points = [
        (slices1[0].centroid.x, slices1[0].centroid.y),
        (slices1[1].centroid.x, slices1[1].centroid.y),
        (slices2[0].centroid.x, slices2[0].centroid.y),
        (slices2[1].centroid.x, slices2[1].centroid.y)
    ]
    points += new_points
    for i in range(0, len(new_points)):
        parishes_df.append(feature['properties']['name_3'])
        point_names_df.append(feature['properties']['name_3'] + '_' + str(i))
df_points = pd.DataFrame()
df_points['parish'] = parishes_df
df_points['point_name'] = point_names_df
df_points['lat'] = [point[1] for point in points]
df_points['long'] = [point[0] for point in points]
df_points.to_csv('../data/points.csv')