# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 16:03:48 2020

@author: Khamar Uz Zama
"""
import readMopexData as md
import readPrismData as pd
import readNoaaData as nd
import helper as hp

fromYear = 1990
toYear = 2000

def getCumulativePrecipitation(fromYear, toYear):
    ppt_cumulative = {}

    # Step 1: Get the required basins
    all_basin_geoms = hp.get_all_basin_coords(mopexOnly=True)
    
    # Step 3: Extract true precipitation from Mopex
    mopex_ppt_data = md.get_mopex_monthly_average()
    
    for yy in range(fromYear, toYear):
        for mm in range(1, 13):
            if(mm<10):
                mmyy = '0'+str(mm)+'-'+str(yy)
            else:
                mmyy = str(mm)+'-'+str(yy)
            
            # Step 2: Calculate Precipitation data from Prism dataset
            prism_basin_ppt_data = pd.get_intersected_basins_ppt_data(all_basin_geoms , month=mm, year=yy, conv2Inches=True)
            
            # Step 4: Extract true precipitation from NOAA
            noaa_basin_ppt_data = nd.get_intersected_basins_ppt_data(all_basin_geoms, month=mm, year=yy)
            
            # Step 5: Combine all three
            allThree_df = hp.zipAllThree(noaa_basin_ppt_data, prism_basin_ppt_data, mopex_ppt_data, mm, yy)
            
            # Step 6: Plot the results
            #hp.plotAllThree(allThree_df, mm, yy)
            ppt_cumulative[mmyy] = allThree_df
            
    return ppt_cumulative




#np.save('1990-2000.npy', ppt_cumulative) 
#read_dictionary = np.load('my_file.npy',allow_pickle='TRUE').item()

ppt_cumulative = getCumulativePrecipitation(fromYear, toYear)

hp.plotRandom(ppt_cumulative)