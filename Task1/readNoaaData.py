# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 02:28:35 2020

@author: Khamar Uz Zama
"""

import numpy as np
import xarray as xr
import geopandas as gpd
import folium
import config as cf
import helper as hp

from os.path import isfile, join
from os import listdir
from folium.plugins import HeatMap


gSpatialIndex = 0

def getNOAAFileNames():    
    noaa_file_names = [f for f in listdir(join(cf.root, cf.noaa_dir)) if isfile(join(cf.root, cf.noaa_dir, f))]
    
    return noaa_file_names


def getNOAAData(month, year, returnGDF, returnDaily):
    
    noaa_file_names = getNOAAFileNames()
    
    if(month<10):
        fileName = "prcp-"+str(year)+"0"+str(month)+"-grd-scaled.nc"
    else:
        fileName = "prcp-"+str(year)+str(month)+"-grd-scaled.nc"
    
    if(fileName not in noaa_file_names):
        print("Data not found for given month and year in NOAA dataset")
        print("month=", month)
        print("year=", year)
        return None
    dnc = xr.open_dataset(join(cf.root, cf.noaa_dir, fileName))  
    df = dnc.to_dataframe()
    df = df.reset_index()
    
    if(returnDaily and returnGDF):
        # Return daily ppt without aggregating over month
        crs = {'init': 'epsg:4326'}
        gdf = gpd.GeoDataFrame(df, crs = crs, geometry=gpd.points_from_xy(df.lon, df.lat))        
        return gdf
    
    df = df.groupby(['lat', 'lon']).agg({'prcp': [np.nanmean]}).reset_index()
    df.columns = ['lat', 'lon', 'prcp']

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

def get_intersected_basins_ppt_data(all_basin_geoms, ppt_gdf, month, year):
    """ Return the precipitation data for basins that intersect with prism grid """
    
    global gSpatialIndex
    print("Processing NOAA Dataset")
    print("-Extracting precipitation data")
    
    intersected_basins = {}
    print("--Creating Spatial RTree Index for month:", month)
    
    # Create a copy of a global index to reduce time.
    # Check if it works correctly.
    
#    if(gSpatialIndex == 0):
#        gSpatialIndex = ppt_gdf.sindex

    print("-Creating basin intersections")
    for basin_file_name, basin_geom in all_basin_geoms.items():
        possible_matches_index = list(ppt_gdf.sindex.intersection(basin_geom.bounds))
        possible_matches = ppt_gdf.iloc[possible_matches_index]
        precise_matches = possible_matches[possible_matches.intersects(basin_geom)]
        
        intersected_basins[basin_file_name] = precise_matches
        
    print("Completed processing")
    return intersected_basins


def getYearlyNoaa(all_basin_geoms, fromYear, toYear):
    """
    Calculates Noaa data for the given years for all the months
    """
    
    yearly_NOAA = {}
    for yy in range(fromYear, toYear):
        print("Processing year", yy)
        for mm in range(1, 3):
            print("Processing month", mm)            
            if(mm<10):
                mmyy = '0'+str(mm)+'-'+str(yy)
            else:
                mmyy = str(mm)+'-'+str(yy)
            print(mmyy)
            ppt_data = getNOAAData(month=mm, year=yy,  returnGDF = True, returnDaily = False)
            yearly_NOAA[mmyy] = get_intersected_basins_ppt_data(all_basin_geoms, ppt_data, month=mm, year=yy)
    
    return yearly_NOAA


def getDailyNoaa(all_basin_geoms, fromYear, toYear):
    """
    Calculates Daily average precipitation
    """
    
    yearly_NOAA = {}
    for yy in range(fromYear, toYear):
        print("Processing year", yy)
        for mm in range(1, 3):
            print("Processing month", mm)            
            if(mm<10):
                mmyy = '0'+str(mm)+'-'+str(yy)
            else:
                mmyy = str(mm)+'-'+str(yy)
            print(mmyy)
            ppt_data = getNOAAData(month=mm, year=yy,  returnGDF = True, returnDaily = True)
            yearly_NOAA[mmyy] = get_intersected_basins_ppt_data(all_basin_geoms, ppt_data, month=mm, year=yy)
    
    return yearly_NOAA


all_basin_geoms = hp.get_all_basin_coords(cf.mopexOnly)
zzz = getDailyNoaa(all_basin_geoms, fromYear = 1990, toYear = 1991)




#getYearlyNoaa(all_basin_geoms, fromYear = 1990, toYear = 1991)
#noaa_file_names = getNOAAFileNames()
#noaaDF = getNOAAData(month=1, year=1987,  returnGDF = False, returnDaily = False)
#plotNOAADataset(noaaDF)
