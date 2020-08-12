import geopandas as gpd
import folium
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join
from shapely.geometry import Polygon, Point

import matplotlib.pyplot as plt
import os

root = "C://Users//user//Desktop//Helmholtz//Tasks//Task 2//"
fileName = "stat_SA.csv"

df = pd.read_csv(os.path.join(root, fileName))

crs = {'init': 'epsg:4326'}
m = folium.Map(zoom_start=10, tiles='cartodbpositron')

geometry = [Point(xy) for xy in zip(df["LATITUDE"], df["LONGITUDE"])]

polygon = gpd.GeoDataFrame(crs=crs, geometry=geometry[:10])

folium.GeoJson(polygon).add_to(m)
folium.LatLngPopup().add_to(m)

m