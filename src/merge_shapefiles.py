import geopandas as gpd
import json as json
import pandas as pd

df_mapping = pd.read_csv('../data/shapefile_mapping.csv')
df_parishes = pd.read_csv('../data/parishes.csv')
with open('../data/parish_shapefile.json', 'r') as f:
    shapes = json.load(f)

parish_include = df_parishes[df_parishes['include']]['parish'].values
df_mapping_filtered = df_mapping[[x in parish_include for x in df_mapping['parish']]]
child_parishes = [x for x in df_mapping_filtered['shapefile']]
parent_parishes = [x for x in df_mapping_filtered['parish']]
municipalities = df_mapping_filtered['municipality'].unique()
parish_mapping = dict(zip([x for x in df_mapping_filtered['shapefile']], [x for x in df_mapping_filtered['parish']]))

# Filter shapes to Porto
features_porto = []
for feature in shapes['features']:
    if feature['properties']['name_2'] in municipalities and feature['properties']['name_3'] in child_parishes:
        features_porto.append(feature)
shapes_porto = shapes
shapes_porto['features'] = features_porto

gdf = gpd.GeoDataFrame.from_features(features_porto)
child_index = dict(zip([x['properties']['name_3'] for x in shapes_porto['features']],[x for x in range(0,len(shapes_porto['features']))]))
parent_children_indices = {}
for x in parent_parishes:
    parent_children_indices[x] = []
for child, parent in parish_mapping.items():
    parent_children_indices[parent].append(child_index[child])



# Merge shape files
features_merged = []
gdf_new = gdf.drop(gdf.index)
for parish in parent_children_indices.keys():
    filtered_gdf = gdf[gdf.index.isin(parent_children_indices[parish])]
    if len(parent_children_indices[parish]) > 1:
        union_geometry = filtered_gdf.geometry.unary_union
        union_gdf = gpd.GeoDataFrame(geometry=[union_geometry], crs=filtered_gdf.crs)
        # Merge any other relevant attributes from the original GeoDataFrame
        for column in filtered_gdf.columns:
            if column != 'geometry':
                if column == 'name_3':
                    union_gdf[column] = parish
                else:
                    union_gdf[column] = filtered_gdf[column][min(parent_children_indices[parish])]
        gdf_new = gdf_new.append(union_gdf)
    else:
        gdf_new = gdf_new.append(filtered_gdf)


gdf_new_json = gdf_new.to_json()
with open('../data/parish_shapefile_merged.json', 'w') as f:
    json.dump(json.loads(gdf_new_json), f)
