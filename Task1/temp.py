# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 12:40:32 2020

@author: Khamar Uz Zama
"""
import geopandas as gpd
import folium
import pandas as pd

from os import listdir
from os.path import isfile, join
from shapely.geometry import Polygon

root = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//"
basins_dir = "Basin_Boundaries//"
basin_file_names = [f for f in listdir(join(root, basins_dir)) if isfile(join(root, basins_dir, f))]

#basin_file_names = ["01010000.BDY", "01010500.BDY","01011000.BDY"]

m = folium.Map(zoom_start=10, tiles='cartodbpositron')

all_basin_geoms = []
for file_name in basin_file_names[:]:
    lat_point_list = []
    lon_point_list = []
    df = pd.read_csv(join(root, basins_dir, file_name), delim_whitespace=True, header=None, skiprows=1)
    lat_point_list = df[1]
    lon_point_list = df[0]

    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
    all_basin_geoms.append(polygon_geom)
    
#    crs = {'init': 'epsg:4326'}
#    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])       
#
#    folium.GeoJson(polygon).add_to(m)
#    folium.LatLngPopup().add_to(m)
m

import numpy as np
 
def read_prism_hdr(hdr_path):
    """Read an ESRI BIL HDR file"""
    with open(hdr_path, 'r') as input_f:
        header_list = input_f.readlines()
    return dict(item.strip().split() for item in header_list)
 
def read_prism_bil(bil_path):
    """Read an array from ESRI BIL raster file"""
    hdr_dict = read_prism_hdr(bil_path.replace('.bil', '.hdr'))
    
    prism_array = np.fromfile(bil_path, dtype=np.float32)
    prism_array = prism_array.reshape(
        int(hdr_dict['NROWS']), int(hdr_dict['NCOLS']))
    prism_array[prism_array == float(hdr_dict['NODATA'])] = np.nan
    return prism_array



prism_dir = "PRISM_ppt_stable_4kmM3_198101_202001_bil//"
prism_file_path = "PRISM_ppt_stable_4kmM3_198103_bil.bil"

prism_array = read_prism_bil(join(root, prism_dir, prism_file_path))

hdr_dict = read_prism_hdr(join(root, prism_dir, prism_file_path).replace('.bil', '.hdr'))

hdr_dict["ULXMAP"] = float(hdr_dict["ULXMAP"])
hdr_dict["ULYMAP"] = float(hdr_dict["ULYMAP"])
hdr_dict['NROWS'] = int(hdr_dict['NROWS'])
hdr_dict['NCOLS'] = int(hdr_dict['NCOLS'])
hdr_dict['XDIM'] = float(hdr_dict['XDIM'])
hdr_dict['YDIM'] = float(hdr_dict['YDIM'])

p1 = (hdr_dict["ULXMAP"] - (hdr_dict['XDIM']/2), 
      hdr_dict["ULYMAP"] + (hdr_dict['XDIM']/2))
	  
p2 = (hdr_dict["ULXMAP"] + hdr_dict['NCOLS']*hdr_dict['XDIM'],
      hdr_dict["ULYMAP"] + (hdr_dict['XDIM']/2))
	  
p3 = (hdr_dict["ULXMAP"] + hdr_dict['NCOLS']*hdr_dict['XDIM'],
      hdr_dict["ULYMAP"] - hdr_dict['NROWS']*hdr_dict['YDIM'])
	  
p4 = (hdr_dict["ULXMAP"] - (hdr_dict['XDIM']/2),
      hdr_dict["ULYMAP"] - hdr_dict['NROWS']*hdr_dict['YDIM'])

lon_point_list = (p1[0], p2[0], p3[0], p4[0])
lat_point_list = (p1[1], p2[1], p3[1], p4[1])
    
polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
crs = {'init': 'epsg:4326'}
polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])       

m = folium.Map(zoom_start=10, tiles='cartodbpositron')

folium.GeoJson(polygon).add_to(m)
folium.LatLngPopup().add_to(m)
m

import rasterio
rasterio.mask.mask(dataset=prism_array,
                   shapes=all_basin_geoms)