# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 16:03:48 2020

@author: Khamar Uz Zama
"""
import readMopexData as md
import readPrismData as pd
import readNoaaData as nd

mm = 1
yy = 1987

dd = md.get_mopex_monthly_average()
noaaDF = nd.getNOAAData(month=mm, year=yy, returnGDF = False)

all_basin_geoms = pd.get_all_basin_coords()
ppt_bounds, ppt_data, hdr_dict = pd.get_monthly_prism_ppt_data(year=yy,month=mm, plotPPTBounds=True)
ppt_gdf = pd.convert_pptData_to_GDF(ppt_bounds, ppt_data, hdr_dict)
intersected_basins = pd.get_intersected_basins(all_basin_geoms, month=mm, year=yy)