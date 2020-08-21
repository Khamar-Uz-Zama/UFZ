# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 16:43:19 2020

@author: Khamar Uz Zama
"""

import pandas as pd
import numpy as np

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