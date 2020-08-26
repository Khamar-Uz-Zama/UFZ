# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 16:43:19 2020

@author: Khamar Uz Zama
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import config as cf

from os import listdir
from os.path import isfile, join
from shapely.geometry import Polygon

def zip_mopex_and_prism(mopex_ppt_data, prism_ppt_data, month, year): 
    trueVSCalc = pd.DataFrame(columns=['Name','Calculated', 'Actual', "Year", "Month"])
    
    for file_name, calculated_ppt in prism_ppt_data.items():
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


def get_all_basin_coords(mopexOnly = False):
    """
    Retrieve basin coordinates and their names
        Three options for reading boundaries:
        1. Read all the basins in Basin_Boundaries
        2. Read only the basins that are present in Mopex dataset
        3. Read only the basins given in documentation
        
    """
        

    #Read basins present in Mopex dataset
    if(mopexOnly):
        basin_file_names = [f.replace('.txt', '.BDY') for f in listdir(join(cf.root, cf.mopex_dir)) if isfile(join(cf.root, cf.mopex_dir, f))]
        basin_file_names = basin_file_names[:-2]
    else:
        #Read basins from Basin_Boundaries directory
        basin_file_names = [f for f in listdir(join(cf.root, cf.basins_dir)) if isfile(join(cf.root, cf.basins_dir, f))]
    
    # Preliminary basins prescribed in documentation
    # basin_file_names = ["11501000.BDY", "12098500.BDY", "08032000.BDY", "11025500.BDY", "03448000.BDY", "01372500.BDY", "05471500.BDY"]
    all_basin_geoms = []
    print("Reading basin coordinates")
    for file_name in basin_file_names[:]:
        lat_point_list = []
        lon_point_list = []
        df = pd.read_csv(join(cf.root, cf.basins_dir, file_name), delim_whitespace=True, header=None, skiprows=1)
        lat_point_list = df[1]
        lon_point_list = df[0]
    
        polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
        all_basin_geoms.append(polygon_geom)
        
    print("Completed reading basins coordinates")

    return dict(zip(basin_file_names, all_basin_geoms))

def zipAllThree(noaa_basin_ppt_data, prism_basin_ppt_data, mopex_ppt_data, month, year):
    """
        Summarizes the data from all the three sources into a single dataframe
    """
    
    print("Summarizing data")
    df = pd.DataFrame(columns=['Basin','Noaa' ,'Prism' , 'Mopex'])
    i=0
    for basin, noaaDF in noaa_basin_ppt_data.items():
        
        temp = []
        temp.append(basin)
        temp.append(noaaDF['prcp'].mean())
        prismDF = prism_basin_ppt_data[basin]
        temp.append(prismDF['Precipitation'].mean())
        basin = basin.replace(".BDY",".txt")
        mopexDF = mopex_ppt_data[basin]
        mopexDF = mopexDF[(mopexDF.index.month == month)]
        mopexDF = mopexDF[(mopexDF.index.year == year)]
        
        if(mopexDF.shape[0] != 1):
            # -1 Indicates that for this month,year and this basin the data is 
            # not available
            mopexPPT = np.nan
        else:
            mopexPPT = mopexDF["precipitation"][0]
        temp.append(mopexPPT)
        
        df.loc[i] = temp
        i+= 1
        
    return df

def plotAllThree(allThree_df, mm, yy):
    """
        Plot precipitation data for given month and year
    """
    print("Visualizing results")
    
    fig, ax = plt.subplots()
    
    ax.plot(allThree_df['Basin'], allThree_df['Noaa'], label="Noaa")
    ax.plot(allThree_df['Basin'], allThree_df['Prism'], label="Prism")
    ax.plot(allThree_df['Basin'], allThree_df['Mopex'], label="Mopex")
    
    # Remove labels
    ax.set_xticklabels([])
    
    title = 'Precipitation data for month =' + str(mm) + ' and year = ' + str(yy)
    ax.title.set_text(title)
    
    ax.legend()
    print("Visualizing complete")
    plt.show()
    
def plotRandom(ppt_cumulative, returnRandom):
    """
        Plots precipitation data for random month and year
    """
    import random
    
    my = random.choice(list(ppt_cumulative.keys()))
    
    month = int(my[:2])
    year = int(my[3:])
    
    plotAllThree(ppt_cumulative[my], month, year)
    
    if(returnRandom):
        return ppt_cumulative[my], month, year
    else:
        return None

def plot_ppt_Metrics(cumulative_cor_Noaa_Mopex, cumulative_cor_Prism_Mopex):
    """
        Plot the given metrics
    """
    print("Visualizing results")
    
    fig, ax = plt.subplots()
    
    ax.plot(cumulative_cor_Noaa_Mopex.keys(), cumulative_cor_Noaa_Mopex.values(), label="NOAA vs Mopex")
    ax.plot(cumulative_cor_Prism_Mopex.keys(), cumulative_cor_Prism_Mopex.values(), label="Prism vs Mopex")
    
    # Remove labels
    ax.set_xticklabels([])
    
    title = 'Correlation plot'
    ax.title.set_text(title)
    
    ax.legend()
    print("Visualizing complete")
    plt.show()
    
    
def calculateMetrics(ppt_cumulative, plotMetrics):
    """
        o. Calculate the following metrics between Noaa and Prism
            1. Pearson Correlation
            2. Mean Absolute error
            3. Mean Squared error
            
        o. Plot the results if required
    """
    from scipy.stats.stats import pearsonr   

    cumulative_cor_Prism_Mopex = {}
    cumulative_cor_Noaa_Mopex = {}
    i = 0
    for key, ppt_data in ppt_cumulative.items():
        
        ppt_data = ppt_data.dropna()
        #cumulative_cor[key] = pearsonr(ppt_data['Noaa'], ppt_data['Prism'])[0]
        cumulative_cor_Noaa_Mopex[key] = pearsonr(ppt_data['Noaa'], ppt_data['Mopex'])[0]
        cumulative_cor_Prism_Mopex[key] = pearsonr(ppt_data['Prism'], ppt_data['Mopex'])[0]
        
#        cumulative_mae[key] = mean_absolute_error(ppt_data['Noaa'], ppt_data['Prism'])
#        cumulative_mse[key] = mean_squared_error(ppt_data['Noaa'], ppt_data['Prism'])
        
        if(i%10 == 0):
            print(i)
        i += 1
    
    if(plotMetrics):
        plot_ppt_Metrics(cumulative_cor_Noaa_Mopex, cumulative_cor_Prism_Mopex)
    return cumulative_cor_Noaa_Mopex, cumulative_cor_Prism_Mopex