# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 13:44:09 2020

@author: Khamar Uz Zama
"""
import geopandas as gpd
import folium
import pandas as pd
import numpy as np

from os.path import join
from shapely.geometry import Polygon

root = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//"
gSpatialIndex = 0

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

    p2 = (p1[0] + (hdr_dict['NCOLS']*hdr_dict['XDIM']),
          p1[1])

    p3 = (p2[0],
          p2[1] - (hdr_dict['NROWS']*hdr_dict['YDIM']))

    p4 = (p1[0],
          p3[1])
    
    lon_point_list = (p1[0], p2[0], p3[0], p4[0])
    lat_point_list = (p1[1], p2[1], p3[1], p4[1])
        
    ppt_bounds = Polygon(zip(lon_point_list, lat_point_list))
    
    if(plotPPTBounds):
        crs = {'init': 'epsg:4326'}
        m = folium.Map(zoom_start=10, tiles='cartodbpositron')
        polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[ppt_bounds])       
    
        folium.GeoJson(polygon).add_to(m)
        folium.LatLngPopup().add_to(m)
        m.save("Prism Bounds.html")

    return ppt_bounds, ppt_data, hdr_dict


def convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict, plotHeatMap):
    """ Convert precipitation data to Geo DataFrame """
    Xmin, Ymin, Xmax, Ymax = ppt_bounds.bounds
    
    Xlength = int((Xmax - Xmin)/hdr_dict['XDIM'])
    Ylength = int((Ymax - Ymin)/hdr_dict['YDIM'])
    
    xx, yy = np.meshgrid(np.linspace(Xmin, Xmax, Xlength), np.linspace(Ymax, Ymin, Ylength))
    xc = xx.flatten()
    yc = yy.flatten()
    ppt_data = ppt_data.flatten()

    df = pd.DataFrame(
        {'Precipitation': ppt_data,
         'Latitude': yc,
         'Longitude': xc})
    
    if(plotHeatMap):
        
        from folium.plugins import HeatMap
        m = folium.Map(zoom_start=10, tiles='cartodbpositron')
        HeatMap(data=df[['Latitude', 'Longitude', 'Precipitation']].groupby(['Latitude', 'Longitude']).sum().reset_index().values.tolist(), radius=8, max_zoom=13).add_to(m)
        folium.LatLngPopup().add_to(m)

        m.save("Prism Heatmap.html")

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
        
    return gdf

def get_intersected_basins_ppt_data(all_basin_geoms , month, year, conv2Inches):
    """ Return the precipitation data for basins that intersect with prism grid """
    
    global gSpatialIndex
    print("Processing Prism Dataset")
    ppt_bounds, ppt_data, hdr_dict = get_monthly_prism_ppt_data(year = year, month = month, plotPPTBounds = False)
    print("-Extracting precipitation data")
    ppt_gdf = convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict, plotHeatMap = False)

    intersected_basins = {}
    print("---Creating Spatial RTree Index for month:", month)
    
    # Create a copy of a global index to reduce time.
    # Check if it works correctly.
    
    if(gSpatialIndex == 0):
        gSpatialIndex = ppt_gdf.sindex

    print("-Creating basin intersections")
    for basin_file_name, basin_geom in all_basin_geoms.items():
        possible_matches_index = list(gSpatialIndex.intersection(basin_geom.bounds))
        possible_matches = ppt_gdf.iloc[possible_matches_index]
        precise_matches = possible_matches[possible_matches.intersects(basin_geom)]
        if(conv2Inches):
            precise_matches["Precipitation"] = precise_matches["Precipitation"]/25.4
        intersected_basins[basin_file_name] = precise_matches
    
    print("Completed processing ")
    return intersected_basins
 
#all_basin_geoms = get_all_basin_coords()
#ppt_bounds, ppt_data, hdr_dict = get_monthly_prism_ppt_data(year=1987,month=1, plotPPTBounds=True)
#ppt_gdf = convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict)
#intersected_basins = get_intersected_basins(all_basin_geoms, month=1, year=1987)