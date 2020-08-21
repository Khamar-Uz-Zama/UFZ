# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 02:28:35 2020

@author: Khamar Uz Zama
"""

from os.path import isfile, join
from os import listdir
import numpy as np
import xarray as xr
import geopandas as gpd
import folium
from folium.plugins import HeatMap

root = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//"
noaa_dir = "NOAA dataset"
gSpatialIndex = 0

def getNOAAFileNames():    
    noaa_file_names = [f for f in listdir(join(root, noaa_dir)) if isfile(join(root, noaa_dir, f))]
    
    return noaa_file_names


def getNOAAData(month, year, returnGDF):
    
    noaa_file_names = getNOAAFileNames()
    
    if(month<10):
        fileName = "prcp-"+str(year)+"0"+str(month)+"-grd-scaled.nc"
    else:
        fileName = "prcp-"+str(year)+str(month)+"-grd-scaled.nc"
    
    if(fileName not in noaa_file_names):
        print("Data not found for given month and year in NOAA dataset")
        return None
    dnc = xr.open_dataset(join(root, noaa_dir, fileName))  
    df = dnc.to_dataframe()
    df = df.reset_index()
    
    df = df.groupby(['lat', 'lon']).agg({'prcp': [np.nanmean]}).reset_index()
    df = df.rename(columns={'prcp.nanmean': 'prcp'})

    if(returnGDF):
        crs = {'init': 'epsg:4326'}
        gdf = gpd.GeoDataFrame(df, crs = crs, geometry=gpd.points_from_xy(df.lon, df.lat))
        return gdf
    else:
        return df

def plotNOAADataset(df):
    """" PLots the heat map of NOAA dataset"""

    m = folium.Map(zoom_start=10, tiles='cartodbpositron')
    
    HeatMap(data=df[['lat', 'lon', 'prcp']].groupby(['lat', 'lon']).sum().reset_index().values.tolist(), radius=8, max_zoom=13).add_to(m)
    m.save("NOAA Heatmap.html")

def get_intersected_basins_ppt_data(all_basin_geoms , month, year):
    """ Return the precipitation data for basins that intersect with prism grid """
    
    global gSpatialIndex
    
    #ppt_bounds, ppt_data, hdr_dict = get_monthly_prism_ppt_data(year = year, month = month, plotPPTBounds = False)
    #ppt_gdf = convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict, plotHeatMap = False)
    ppt_gdf = getNOAAData(month=month, year=year,  returnGDF = True)

    
    
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


    
#noaa_file_names = getNOAAFileNames()
#noaaDF = getNOAAData(month=1, year=1987,  returnGDF = False)
#plotNOAADataset(noaaDF)

