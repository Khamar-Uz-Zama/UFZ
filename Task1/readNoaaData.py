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

def getNOAAFileNames():    
    noaa_file_names = [f for f in listdir(join(root, noaa_dir)) if isfile(join(root, noaa_dir, f))]
    
    return noaa_file_names


def getNOAAData(month, year, returnGDF):
    
    
    if(month<10):
        fileName = "prcp-"+str(year)+"0"+str(month)+"-grd-scaled.nc"
    else:
        fileName = "prcp-"+str(year)+str(month)+"-grd-scaled.nc"
    
    if(fileName not in noaa_file_names):
        print("Data not found for given month and year in NOAA dataset")
        
    dnc = xr.open_dataset(join(root, noaa_dir, fileName))  
    df = dnc.to_dataframe()
    df = df.reset_index()
    
    df = df.groupby(['lat', 'lon']).agg({'prcp': [np.nanmean]}).reset_index()
    
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
    
#noaa_file_names = getNOAAFileNames()
#noaaDF = getNOAAData(month=1, year=1987,  returnGDF = False)
#plotNOAADataset(noaaDF)