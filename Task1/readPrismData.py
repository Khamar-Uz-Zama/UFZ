# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 13:44:09 2020

@author: Khamar Uz Zama
"""
import geopandas as gpd
import folium
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join
from shapely.geometry import Polygon

import matplotlib.pyplot as plt
import os

root = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//"
gSpatialIndex = 0

def get_all_basin_coords():
    """
    Retrieve basin coordinates and their names
        Three options for reading boundaries:
        1. Read all the basins in Basin_Boundaries
        2. Read only the basins that are present in Mopex dataset
        3. Read only the basins given in documentation
        
    """
        
    basins_dir = "Basin_Boundaries//"
    mopex_dir = "MOPEX//"
    
    # Read basins from Basin_Boundaries directory
    #basin_file_names = [f for f in listdir(join(root, basins_dir)) if isfile(join(root, basins_dir, f))]
    
    #Read basins present in Mopex dataset
    basin_file_names = [f.replace('.txt', '.BDY') for f in listdir(join(root, mopex_dir)) if isfile(join(root, mopex_dir, f))]
    basin_file_names = basin_file_names[:-2]
    
    # Preliminary basins prescribed in documentation
    # basin_file_names = ["11501000.BDY", "12098500.BDY", "08032000.BDY", "11025500.BDY", "03448000.BDY", "01372500.BDY", "05471500.BDY"]
    all_basin_geoms = []
    print("Reading basin coordinates")
    for file_name in basin_file_names[:]:
        lat_point_list = []
        lon_point_list = []
        df = pd.read_csv(join(root, basins_dir, file_name), delim_whitespace=True, header=None, skiprows=1)
        lat_point_list = df[1]
        lon_point_list = df[0]
    
        polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
        all_basin_geoms.append(polygon_geom)
        
    print("Completed reading basins coordinates")

    return dict(zip(basin_file_names, all_basin_geoms))

def read_prism_hdr(hdr_path):
    """ Read an ESRI BIL HDR file
        HDR file contains meta data for the precipitation data
    """    
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

def get_monthly_prism_ppt_data(year,month, plotPPTBounds):
    """ Get precipitation data for given mm, YY from PRISM data"""
    """ It is in the form of grid """
    
    prism_dir = "PRISM_ppt_stable_4kmM3_198101_202001_bil//"
    
    if(month<10):
        prism_file_path = "PRISM_ppt_stable_4kmM3_"+str(year)+"0"+str(month)+"_bil.bil"
    else:
        prism_file_path = "PRISM_ppt_stable_4kmM3_"+str(year)+str(month)+"_bil.bil" 
        
    ppt_data = read_prism_bil(join(root, prism_dir, prism_file_path))
    
    hdr_dict = read_prism_hdr(join(root, prism_dir, prism_file_path).replace('.bil', '.hdr'))
    
    hdr_dict["ULXMAP"] = float(hdr_dict["ULXMAP"])
    hdr_dict["ULYMAP"] = float(hdr_dict["ULYMAP"])
    hdr_dict['NROWS'] = int(hdr_dict['NROWS'])
    hdr_dict['NCOLS'] = int(hdr_dict['NCOLS'])
    hdr_dict['XDIM'] = float(hdr_dict['XDIM'])
    hdr_dict['YDIM'] = float(hdr_dict['YDIM'])
    
    p1 = (hdr_dict["ULXMAP"] - (hdr_dict['XDIM']/2), 
          hdr_dict["ULYMAP"] + (hdr_dict['YDIM']/2))

    p2 = (hdr_dict["ULXMAP"] + (hdr_dict['NCOLS']*hdr_dict['XDIM']),
          hdr_dict["ULYMAP"] + (hdr_dict['XDIM']/2))

    p3 = (hdr_dict["ULXMAP"] + (hdr_dict['NCOLS']*hdr_dict['XDIM']),
          hdr_dict["ULYMAP"] - (hdr_dict['NROWS']*hdr_dict['YDIM']))

    p4 = (hdr_dict["ULXMAP"] - (hdr_dict['XDIM']/2),
          hdr_dict["ULYMAP"] - hdr_dict['NROWS']*hdr_dict['YDIM'])
    
    lon_point_list = (p1[0], p2[0], p3[0], p4[0])
    lat_point_list = (p1[1], p2[1], p3[1], p4[1])
        
    ppt_bounds = Polygon(zip(lon_point_list, lat_point_list))
    
    if(plotPPTBounds):
        crs = {'init': 'epsg:4326'}
        m = folium.Map(zoom_start=10, tiles='cartodbpositron')
        polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[ppt_bounds])       
    
        folium.GeoJson(polygon).add_to(m)
        folium.LatLngPopup().add_to(m)
        m.save("Prism data")

    return ppt_bounds, ppt_data, hdr_dict


def convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict):
    """ Convert precipitation data to Geo DataFrame """
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
        
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    return gdf

def get_intersected_basins(all_basin_geoms , month, year):
    """ Return the precipitation data for basins that intersect with prism grid """
    
    global gSpatialIndex
    ppt_bounds, ppt_data, hdr_dict = get_monthly_prism_ppt_data(year=year, month=month, plotPPTBounds = True)
    ppt_gdf = convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict)

    intersected_basins = {}
    print("Creating Spatial RTree Index for month:", month)
    
    # Create a copy of a global index to reduce time.
    # Check if it works correctly.
    
    if(gSpatialIndex == 0):
        gSpatialIndex = ppt_gdf.sindex

    print("Creating basin intersections")
    for basin_file_name, basin_geom in all_basin_geoms.items():
        possible_matches_index = list(gSpatialIndex.intersection(basin_geom.bounds))
        possible_matches = ppt_gdf.iloc[possible_matches_index]
        precise_matches = possible_matches[possible_matches.intersects(basin_geom)]
        
        intersected_basins[basin_file_name] = precise_matches

    return intersected_basins
 
#all_basin_geoms = get_all_basin_coords()
#ppt_bounds, ppt_data, hdr_dict = get_monthly_prism_ppt_data(year=1987,month=1, plotPPTBounds=True)
#ppt_gdf = convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict)
#intersected_basins = get_intersected_basins(all_basin_geoms, month=1, year=1987)