# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 16:03:48 2020

@author: Khamar Uz Zama
"""
import readMopexData as md
import readPrismData as pd
import readNoaaData as nd
import helper as hp

mm = 1
yy = 1987


# Calculate Precipitation data for Prism dataset
all_basin_geoms = pd.get_all_basin_coords()
prism_basin_ppt_data = pd.get_intersected_basins_ppt_data(all_basin_geoms , month=mm, year=yy, conv2Inches=True)
#
## Extract true precipitation from Mopex
#mopex_ppt_data = md.get_mopex_monthly_average()


# Extract true precipitation from NOAA
#noaa_basin_ppt_data = nd.get_intersected_basins_ppt_data(all_basin_geoms, month=mm, year=yy)




#mVSp = hp.zip_mopex_and_prism(mopex_ppt_data=mopex_ppt_data, prism_ppt_data=prism_basin_ppt_data, month=mm, year=yy)