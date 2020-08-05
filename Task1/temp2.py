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


def get_all_basin_coords():
    """Retrieve basin coordinates and their names"""
    basins_dir = "Basin_Boundaries//"
    mopex_dir = "MOPEX//"
    
    #basin_file_names = [f for f in listdir(join(root, basins_dir)) if isfile(join(root, basins_dir, f))]
    # below basins are present in mopex dataset
    basin_file_names = [f.replace('.txt', '.BDY') for f in listdir(join(root, mopex_dir)) if isfile(join(root, mopex_dir, f))]
    basin_file_names = basin_file_names[:-2]
    #basin_file_names = ["01048000.BDY", "01055500.BDY","01060000.BDY", "01064500.BDY", "01076500.BDY"]
        
    all_basin_geoms = []
    for file_name in basin_file_names[:]:
        lat_point_list = []
        lon_point_list = []
        df = pd.read_csv(join(root, basins_dir, file_name), delim_whitespace=True, header=None, skiprows=1)
        lat_point_list = df[1]
        lon_point_list = df[0]
    
        polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
        all_basin_geoms.append(polygon_geom)
         
    return all_basin_geoms, basin_file_names

 
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


def get_intersected_basins():
    """ Return the basins precipitation data that intersect with prism data """
    
    all_basin_geoms, basin_file_names = get_all_basin_coords()
    ppt_bounds, ppt_data, hdr_dict = get_monthly_prism_ppt_data(year=1987, month=8)
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
    #clipped = gpd.clip(gdf=ppt_gdf, mask=all_basin_geoms[0])
    print("Creating Index")
    spatial_index = ppt_gdf.sindex
    
    for count, basin_geom in enumerate(all_basin_geoms):
        print("Index", count)
        print("basin_file_name:", basin_file_names[count])    
        possible_matches_index = list(spatial_index.intersection(basin_geom.bounds))
        possible_matches = ppt_gdf.iloc[possible_matches_index]
        precise_matches = possible_matches[possible_matches.intersects(basin_geom)]
        
        intersected_basins[basin_file_names[count]] = precise_matches

    return intersected_basins
    

def get_mopex_average():
    """ Get average precipitation data for all the basins in mopex """
    mopex_dir = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//MOPEX"
    basin_file_names = [f for f in listdir(join(root, mopex_dir)) if isfile(join(root, mopex_dir, f))]
    basin_file_names = basin_file_names[:-2]

    mopex_data = {}
    for count, file_name in enumerate(basin_file_names):
        print(count)
        mopex_df = pd.read_csv(os.path.join(mopex_dir, file_name))
        mopex_df = mopex_df[["precipitation", "month", "year", "date"]]
        mopex_df['date'] = pd.to_datetime(mopex_df['date'])
        
    #    start_date = '01-01-1987'
    #    end_date = '30-12-1987'
    #    mask = (mopex_df['date'] > start_date) & (mopex_df['date'] <= end_date)
    #    filtered_mopex_df = mopex_df.loc[mask]
    
        mopex_df.set_index('date', inplace=True)
        mopex_df.index = pd.to_datetime(mopex_df.index)
        monthly_average = mopex_df.resample('1M').mean()
        mopex_data[file_name] = monthly_average

    return mopex_data
    
filtered_mopex = get_mopex_average()
# Remove the basins that have null values - check for all
inter = get_intersected_basins()
notNulls = {}
for name, data_df in inter.items():
    if(not data_df.isnull().values.any()):
        notNulls[name] = data_df

 
trueVSCalc = pd.DataFrame(columns=['Name','Calculated', 'Actual', "Year", "Month"])

for file_name, calculated_ppt in notNulls.items():
    temp = {}
    temp["Name"] = file_name.replace(".BDY","")
    temp["Calculated"] = calculated_ppt["Precipitation"].mean()

    ppt_file_name = file_name.replace(".BDY",".txt")
    true_ppt = filtered_mopex[ppt_file_name]
    
    true_ppt = true_ppt[(true_ppt.index.month == 8)]
    true_ppt = true_ppt[(true_ppt.index.year == 1987)]
    if(len(true_ppt) > 0):
        true_ppt = true_ppt["precipitation"][0]
    else:
        true_ppt = np.nan
    temp["Year"] = 1987
    temp["Month"] = 8
    temp["Actual"] = true_ppt
    trueVSCalc = trueVSCalc.append(temp, ignore_index=True)