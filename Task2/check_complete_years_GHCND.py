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
chile_Dir = "Chile"

def readBasins():
    fileName = "stat_SA.csv"
    df = pd.read_csv(os.path.join(root, fileName))
    
    return df


df = readBasins()
def readFromGHCND_SA():
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
            
    print("Following files could not be read from GHCND_SA")

def extactChile():
    fileName = "cr2_prDaily_2018.txt"
    df_chile = pd.read_csv(os.path.join(root, chile_Dir, fileName))
    
    df_chile = df_chile.drop(df_chile.index[0:14])
        
    basinCodes = list(df_chile.columns.values)
    basinCodes = basinCodes[1:]
    for basinColumn in basinCodes:
        
        zz = df_chile[['codigo_estacion',basinColumn]]
        zz = zz[zz[basinColumn] != "-9999"]
        zz = zz[zz[basinColumn] != -9999]
        #zz = zz.dropna(subset=[basinColumn])
        
        zz['codigo_estacion'] = pd.to_datetime(zz.codigo_estacion)
        yy = zz.groupby([zz['codigo_estacion'].dt.year]).count()
        yy = yy.rename(columns = {"codigo_estacion": "PRCP_days_Count"})
        yy = yy.drop(columns=[basinColumn])

        # drop the basins with less than 330 count
        yy =  yy.drop(yy[yy.PRCP_days_Count < 330].index)


extactChile()
