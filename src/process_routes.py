import json
import pandas as pd
import os
from geopy.distance import distance

DATA_DIR = '../data/routes/'

routes_df = pd.DataFrame()
route_orig = []
route_dest = []
route_mode = []
route_orig_coordinates = []
route_dest_coordinates = []
route_orig_address = []
route_dest_address = []
route_duration = []
route_distance = []
route_distance_route = []
route_polyline = []

route_details_df = pd.DataFrame()
route_details_orig = []
route_details_dest = []
route_details_mode = []
route_details_step = []
route_details_polyline = []

points_df = pd.read_csv('../data/points.csv')
point_lat = dict(zip([x for x in points_df['point_name']], [x for x in points_df['lat']]))
point_long = dict(zip([x for x in points_df['point_name']], [x for x in points_df['long']]))
point_parish = dict(zip([x for x in points_df['point_name']], [x for x in points_df['parish']]))

for filename in os.listdir(DATA_DIR):
    if filename.endswith('.json'):
        with open(os.path.join(DATA_DIR, filename), 'r') as f:
            orig = filename.split('_')[0]
            dest = filename.split('_')[1]
            mode = filename.split('_')[2][0:-5]
            routes = json.load(f)
            durations = [route['legs'][0]['duration']['value'] for route in routes]
            if routes:
                duration_min_index = durations.index(min(durations))
                best_route = routes[duration_min_index]
                leg = best_route['legs'][0]
                duration = leg['duration']['value']
                distance_route = sum([step['distance']['value'] for step in leg['steps']])
            else:
                duration = None
                distance_route = None
            orig_coordinates = (point_lat[orig], point_long[orig])
            dest_coordinates = (point_lat[dest], point_long[dest])
            distance_m = distance(orig_coordinates, dest_coordinates).km * 1000
            # Update dataframe:
            route_orig.append(orig)
            route_dest.append(dest)
            route_mode.append(mode)
            route_orig_address.append(leg['start_address'])
            route_dest_address.append(leg['end_address'])
            route_orig_coordinates.append(orig_coordinates)
            route_dest_coordinates.append(dest_coordinates)
            route_duration.append(duration)
            route_distance.append(distance_m)
            route_distance_route.append(distance_route)
            if routes:
                for s in range(0, len(leg['steps'])):
                    step = leg['steps'][s]
                    route_details_orig.append(orig)
                    route_details_dest.append(dest)
                    route_details_mode.append(mode)
                    route_details_step.append(s)
                    route_details_polyline.append(step['polyline']['points'])

routes_df['orig'] = route_orig
routes_df['orig_parish'] = [point_parish[point] for point in route_orig]
routes_df['dest'] = route_dest
routes_df['dest_parish'] = [point_parish[point] for point in route_dest]
routes_df['mode'] = route_mode
routes_df['orig_coordinates'] = route_orig_coordinates
routes_df['dest_coordinates'] = route_dest_coordinates
routes_df['orig_address'] = route_orig_address
routes_df['dest_address'] = route_dest_address
routes_df['duration'] = route_duration
routes_df['distance'] = route_distance
routes_df['distance_route'] = route_distance_route

route_details_df['orig'] = route_details_orig
route_details_df['dest'] = route_details_dest
route_details_df['mode'] = route_details_mode
route_details_df['step'] = route_details_step
route_details_df['polyline'] = route_details_polyline

routes_df.to_csv('../data/routes.csv', index=False)
route_details_df.to_csv('../data/route_details.csv', index=False)
