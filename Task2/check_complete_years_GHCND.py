import geopandas as gpd
import folium
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join
from shapely.geometry import Polygon, Point

import matplotlib.pyplot as plt
import os

root = "C://Users//user//Desktop//Helmholtz//Tasks//Task 2//"
ghcnd_Dir = "GHCND_SA"

def readBasins():

    fileName = "stat_SA.csv"
    df = pd.read_csv(os.path.join(root, fileName))
    
    return df


df = readBasins()

completeBasins = {}
completeBasinsCount = {} 
unreadableFiles = []
for index, row in df.iterrows():
    try:
        if(index%100 == 0):
            print(index)
        basinName = row.iloc[0] + ".csv"
    
        basinHistory = pd.read_csv(os.path.join(root, ghcnd_Dir, basinName))
        
        basinHistoryWOna = basinHistory.dropna(subset=['PRCP'])
        
        if(basinHistoryWOna.shape[0] != basinHistory.shape[0]):
            print("Sanity check")
        
        zz = basinHistoryWOna[["year","PRCP"]].groupby("year").count().reset_index()
        zz = zz.rename(columns = {"PRCP": "PRCP_days_Count"})

        # drop the basins with less than 330 count
        zzz =  zz.drop(zz[zz.PRCP_days_Count < 330].index)
        
        completeBasinsCount[basinName] = zzz.shape[0]
        
        if(zzz.shape[0] > 30):
            completeBasins[basinName] = zzz  
    except :
        unreadableFiles.append(basinName)
        
print("Following files could not be read")
print(unreadableFiles)
