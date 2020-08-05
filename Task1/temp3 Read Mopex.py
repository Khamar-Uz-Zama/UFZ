# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 23:18:25 2020

@author: Khamar Uz Zama
"""

import pandas as pd
import os
import geopandas as gpd
import folium
import pandas as pd
import numpy as np



from os import listdir
from os.path import isfile, join
from shapely.geometry import Polygon



root = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//"
basins_dir = "Basin_Boundaries//"
#basin_file_names = [f for f in listdir(join(root, basins_dir)) if isfile(join(root, basins_dir, f))]

# below basins are present in mopex dataset
basin_file_names = ["01048000.BDY"]#, "01055500.BDY","01060000.BDY"]

m = folium.Map(zoom_start=10, tiles='cartodbpositron')

def get_all_basin_coords():
    basins_dir = "Basin_Boundaries//"
    #basin_file_names = [f for f in listdir(join(root, basins_dir)) if isfile(join(root, basins_dir, f))]

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
    #m
    
    return all_basin_geoms

 
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

def get_ppt_data():
    prism_dir = "PRISM_ppt_stable_4kmM3_198101_202001_bil//"
    prism_file_path = "PRISM_ppt_stable_4kmM3_198101_bil.bil"
    
    ppt_data = read_prism_bil(join(root, prism_dir, prism_file_path))
    
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
        
    ppt_bounds = Polygon(zip(lon_point_list, lat_point_list))
    
    return ppt_bounds, ppt_data, hdr_dict

def convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict):
        
    Xmin, Ymin, Xmax, Ymax = ppt_bounds.bounds
    
    Xlength = int((Xmax - Xmin)/hdr_dict['XDIM'])
    Ylength = int((Ymax - Ymin)/hdr_dict['YDIM'])
    
    xx, yy = np.meshgrid(np.linspace(Xmin, Xmax, Xlength), np.linspace(Ymin, Ymax, Ylength))
    xc = xx.flatten()
    yc = yy.flatten()
    ppt_data = ppt_data.flatten()
    
    df = pd.DataFrame(
        {'Precipitation': ppt_data,
         'Latitude': yc,
         'Longitude': xc})
        
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    
    
    return gdf

def get_mopex_data():

    mopex_dir = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//MOPEX"
    file_name = "01048000.txt"
    
    
    mopex_df = pd.read_csv(os.path.join(mopex_dir, file_name))
    mopex_df['date'] = pd.to_datetime(mopex_df['date'])
    
    
    start_date = '01-01-1981'
    end_date = '30-01-1981'
    
    mask = (mopex_df['date'] > start_date) & (mopex_df['date'] <= end_date)
    
    filtered_mopex_df = mopex_df.loc[mask]
    
    return filtered_mopex_df
    
#filtered_moax = get_mopex_data()    
    
    
#all_basin_geoms = get_all_basin_coords()
#ppt_bounds, ppt_data, hdr_dict = get_ppt_data()
#ppt_gdf = convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict)


mopex_dir = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//MOPEX"
file_name = "01048000.txt"


mopex_df = pd.read_csv(os.path.join(mopex_dir, file_name))
mopex_df['date'] = pd.to_datetime(mopex_df['date'])


start_date = '01-01-1987'
end_date = '30-12-1987'

mask = (mopex_df['date'] > start_date) & (mopex_df['date'] <= end_date)

filtered_mopex_df = mopex_df.loc[mask]







