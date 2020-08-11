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
gIndex = 0

def get_all_basin_coords():
    """Retrieve basin coordinates and their names"""
    basins_dir = "Basin_Boundaries//"
    mopex_dir = "MOPEX//"
    
    #basin_file_names = [f for f in listdir(join(root, basins_dir)) if isfile(join(root, basins_dir, f))]
    # below basins are present in mopex dataset
    basin_file_names = [f.replace('.txt', '.BDY') for f in listdir(join(root, mopex_dir)) if isfile(join(root, mopex_dir, f))]
    basin_file_names = basin_file_names[:-2]
    
    #basin_file_names = ["1595000.BDY","1606500.BDY","1608500.BDY","1610000.BDY","1611500.BDY"]

    all_basin_geoms = []
    print("Reading basins coordinates")
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

def get_monthly_prism_ppt_data(year,month):
    """ Get true precipitation data for given mmYY"""
    
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

def plot_basins(basin_geoms):
    """ Plot the given basins """
    crs = {'init': 'epsg:4326'}
    m = folium.Map(zoom_start=10, tiles='cartodbpositron')

    for basin_geom in basin_geoms:
        polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[basin_geom])       

        folium.GeoJson(polygon).add_to(m)
        folium.LatLngPopup().add_to(m)
        
    return m

def convert_basin_geom_to_GDF(basin):
    """ Convert basin geoms to Geo DataFrames """
    
    longs, lats = basin.exterior.coords.xy
    df = pd.DataFrame({'Latitude': longs,
                       'Longitude': lats})
        
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    
    return gdf


def get_intersected_basins(all_basin_geoms , month, year):
    """ Return the precipitation data for basins that intersect with prism grid """
    global gIndex
    ppt_bounds, ppt_data, hdr_dict = get_monthly_prism_ppt_data(year=year, month=month)
    ppt_gdf = convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict)
    
#    all_basin_gdf = []
#    for basin in all_basin_geoms:
#        basin_gdf = convert_basin_geom_to_GDF(basin)
#        all_basin_gdf.append(basin_gdf)    
#    
    #plot_basins(all_basin_geoms)
    #fig, ax = plt.subplots(1, 1)
    #ppt_gdf.plot(column="Precipitation", ax=ax, legend=True)

    intersected_basins = {}
    print("Creating Spatial RTree Index for month:", month)
    
    # Create a copy of a global index to reduce time.
    # Check if it works correctly.
    
    if(gIndex == 0):
        spatial_index = ppt_gdf.sindex
        gIndex = spatial_index
    else:
        spatial_index = gIndex
        
    print("Creating basin intersections")
    for basin_file_name, basin_geom in all_basin_geoms.items():
        possible_matches_index = list(spatial_index.intersection(basin_geom.bounds))
        possible_matches = ppt_gdf.iloc[possible_matches_index]
        precise_matches = possible_matches[possible_matches.intersects(basin_geom)]
        
        intersected_basins[basin_file_name] = precise_matches

    return intersected_basins
    

def get_mopex_monthly_average():
    """ Get average precipitation data for all the basins in mopex  for all the possible years"""
    mopex_dir = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//MOPEX"
    mopex_file_names = [f for f in listdir(join(root, mopex_dir)) if isfile(join(root, mopex_dir, f))]
    # Remove last two files as they contain summaries
    mopex_file_names = mopex_file_names[:-2]

    mopex_data = {}
    print("Reading mopex data")
    for count, file_name in enumerate(mopex_file_names):
        mopex_df = pd.read_csv(os.path.join(mopex_dir, file_name))
        mopex_df = mopex_df[["precipitation", "month", "year", "date"]]
        mopex_df['date'] = pd.to_datetime(mopex_df['date'])
    
        mopex_df.set_index('date', inplace=True)
        mopex_df.index = pd.to_datetime(mopex_df.index)
        monthly_average = mopex_df.resample('1M').mean()
        mopex_data[file_name] = monthly_average
        
    print("Completed reading mopex data")
    return mopex_data
    

def remove_basin_nulls(basins_with_ppt):
    # Remove the basins that have null values - check for all

    notNulls = {}
    for name, data_df in basins_with_ppt.items():
        if(not data_df.isnull().values.any()):
            notNulls[name] = data_df
    
    return notNulls

def zip_calc_and_true(mopex_ppt_data, basins, month, year): 
    trueVSCalc = pd.DataFrame(columns=['Name','Calculated', 'Actual', "Year", "Month"])
    
    for file_name, calculated_ppt in basins.items():
        temp = {}
        temp["Name"] = file_name.replace(".BDY","")
        temp["Calculated"] = calculated_ppt["Precipitation"].mean()
    
        ppt_file_name = file_name.replace(".BDY",".txt")
        true_ppt = mopex_ppt_data[ppt_file_name]
        
        true_ppt = true_ppt[(true_ppt.index.month == month)]
        true_ppt = true_ppt[(true_ppt.index.year == year)]
        if(len(true_ppt) > 0):
            true_ppt = true_ppt["precipitation"][0]
        else:
            true_ppt = np.nan
        temp["Year"] = year
        temp["Month"] = month
        temp["Actual"] = true_ppt
        trueVSCalc = trueVSCalc.append(temp, ignore_index=True)
        
    return trueVSCalc

def filter_basins_by_mopex(mopex_ppt_data, all_basin_geoms):
    """ Remove basins which are not in mopex dataset """
    dict_you_want = {your_key.replace(".txt",".BDY"): all_basin_geoms[your_key.replace(".txt",".BDY")] for your_key in mopex_ppt_data.keys() }
    return dict_you_want
        
def calculate_for_years():
    comparison = pd.DataFrame(columns=['Name','Calculated', 'Actual', "Year", "Month"])
    years = [1987]
    import time
    for y in years:
        Year_start = time.time()
        print("Processing Year =>", y)
        for m in range(1,2):
            month_start = time.time()
            print("Processing Month =>", m)
            basins_with_ppt = get_intersected_basins(all_basin_geoms, month = m, year = y)
            basins = remove_basin_nulls(basins_with_ppt)
            trueVSCalc = zip_calc_and_true(mopex_ppt_data, basins, month=m, year=y)
            comparison = comparison.append(trueVSCalc)
            print("Time taken for  month:", month_start - time.time())
            
        print("Time taken for  year:", Year_start - time.time())
    

    from tkinter import filedialog
    
    export_file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    comparison.to_csv (export_file_path, index = False, header=True)
    
    return comparison, basins




def plot_basins_from_lat_long(basins_with_ppt, basin_name):
    """ Plot the given basins """
    basin_data = basins_with_ppt[basin_name]
    
    lat_point_list = basin_data["Latitude"]
    lon_point_list = basin_data["Longitude"]


    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))

    
    crs = {'init': 'epsg:4326'}
    m = folium.Map(zoom_start=10, tiles='cartodbpositron')

    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])       

    folium.GeoJson(polygon).add_to(m)
    folium.LatLngPopup().add_to(m)
        
    return m


mopex_ppt_data = get_mopex_monthly_average()
all_basin_geoms = get_all_basin_coords()
all_basin_geoms = filter_basins_by_mopex(mopex_ppt_data, all_basin_geoms)
comparison, basins_with_ppt = calculate_for_years()



basin_name = "01606500.BDY"

plot_basins([all_basin_geoms[basin_name]])

plot_basins_from_lat_long(basins_with_ppt, basin_name)
