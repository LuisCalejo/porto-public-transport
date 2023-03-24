import datetime
import googlemaps
import os
import pandas as pd
import pytz
import json


TEST_RUN = False
TEST_POINTS = ['Ramalde1', 'Canidelo1', 'União das freguesias de São Mamede de Infesta e Senhora da Hora1']
API_KEY = os.environ['GOOGLE_MAPS_API_KEY']
TIME_ZONE = pytz.timezone('Europe/Lisbon')
ARRIVAL_TIME = datetime.datetime(2023, 3, 15, 9-1, 30, tzinfo=TIME_ZONE)  # subtract 30 min to offset google api delay
TRANSPORT_MODES = ['walking', 'transit', 'driving']
DATA_DIR = '../data/routes/'
START_FROM = 1

points_df = pd.read_csv('../data/points.csv')

if TEST_RUN:
    points_df = points_df[[x in TEST_POINTS for x in points_df['point_name']]]

points = points_df['point_name'].values
point_lat = dict(zip(points, points_df['lat'].values))
point_long = dict(zip(points, points_df['long'].values))
point_coordinates = dict(
    zip(points, [str(x[0]) + ',' + str(x[1]) for x in zip(points_df['lat'].values, points_df['long'].values)]))
point_parish = dict(zip(points, points_df['parish'].values))

route_count = 0
for orig in points:
    for dest in points:
        if orig != dest:
            for mode in TRANSPORT_MODES:
                route_count += 1
                if route_count >= START_FROM:
                    print("Route number {}: from {} to {} - {}".format(str(route_count), orig, dest, mode))
                    client = googlemaps.Client(API_KEY)
                    start = point_coordinates[orig]
                    end = point_coordinates[dest]
                    directions_result = client.directions(start, end, mode=mode, arrival_time=ARRIVAL_TIME,
                                                          alternatives=True)
                    file_name = orig + '_' + dest + '_' + mode + '.json'
                    with open(DATA_DIR + file_name, 'w') as f:
                        json.dump(directions_result, f)
