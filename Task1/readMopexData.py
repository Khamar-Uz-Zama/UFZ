# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 15:12:54 2020

@author: Khamar Uz Zama
"""

import pandas as pd, os
from os import listdir
from os.path import isfile, join

root = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//"


def get_mopex_monthly_average():
    """ Get average precipitation data for all the basins in mopex  for all the possible years"""
    mopex_dir = "C://Users//user//Desktop//Helmholtz//Tasks//Task 1//MOPEX"
    mopex_file_names = [f for f in listdir(join(root, mopex_dir)) if isfile(join(root, mopex_dir, f))]
    # Remove last two files as they contain summaries
    mopex_file_names = mopex_file_names[:-2]

    mopex_data = {}
    print("Reading mopex data")
    print("-Calculating monthly average")
    for count, file_name in enumerate(mopex_file_names):
        mopex_df = pd.read_csv(os.path.join(mopex_dir, file_name))
        mopex_df = mopex_df[["precipitation", "month", "year", "date"]]
        
        mopex_df['date'] = pd.to_datetime(mopex_df['date'])
        mopex_df.set_index('date', inplace=True)
        
        # The mean excludes the nan rows
        # If there is any row with Nan for a given month, then only that row is removed.
        monthly_average = mopex_df.resample('1M').mean()
        mopex_data[file_name] = monthly_average
        
    print("Completed reading mopex data")
    
    return mopex_data

#get_mopex_monthly_average()