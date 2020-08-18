# What is use of prcp dataset?
# Calculated completeYears for all the basins in Chile dataset
# Calculated completeYears for all the basins in  stat_SA dataset 
import pandas as pd
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
    # Calculate precipitation for the basins present in stat_SA from GHCNDA data
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
            
            #if(basinHistoryWOna.shape[0] != basinHistory.shape[0]):
                #print()
            
            zz = basinHistoryWOna[["year","PRCP"]].groupby("year").count().reset_index()
            zz = zz.rename(columns = {"PRCP": "PRCP_days_Count"})
    
            # drop the basins with less than 330 count
            zzz =  zz.drop(zz[zz.PRCP_days_Count < 330].index)
            
            completeBasinsCount[basinName] = zzz.shape[0]
            
            if(zzz.shape[0] > 30):
                completeBasins[basinName] = zzz
        except :
            unreadableFiles.append(basinName)
            
    return completeBasins
            
    print("Following files could not be read from GHCND_SA")

def extactChile():
    # Calculate ppt for basins present chile dataset
    completeBasins = {}
    completeBasinsCount = {}
    
    fileName = "cr2_prDaily_2018.txt"
    df_chile = pd.read_csv(os.path.join(root, chile_Dir, fileName))
    
    df_chile = df_chile.drop(df_chile.index[0:14])
        
    basinCodes = list(df_chile.columns.values)
    basinCodes = basinCodes[1:]
    i = 0
    for basinColumn in basinCodes:
        if(i%100 == 0):
                print(i)
        df_basin = df_chile[['codigo_estacion',basinColumn]]
        df_basin = df_basin[df_basin[basinColumn] != "-9999"]
        df_basin = df_basin[df_basin[basinColumn] != -9999]
        #zz = zz.dropna(subset=[basinColumn])
        
        df_basin['codigo_estacion'] = pd.to_datetime(df_basin.codigo_estacion)
        df_basin = df_basin.groupby([df_basin['codigo_estacion'].dt.year]).count()
        df_basin = df_basin.rename(columns = {"codigo_estacion": "PRCP_days_Count"})
        df_basin = df_basin.drop(columns=[basinColumn])

        # drop the basins with less than 330 count
        df_basin =  df_basin.drop(df_basin[df_basin.PRCP_days_Count < 330].index)
        completeBasinsCount[basinColumn] = df_basin.shape[0]
        
        # add the basins for more than 30 years
        if(df_basin.shape[0] > 30):
            completeBasins[basinColumn] = df_basin
        i += 1
        
    return completeBasins
    
completeBasins_Chile = extactChile()
completeBasins_GHCND_SA = readFromGHCND_SA()

csvDF = pd.DataFrame(columns=["ID", "Source", "No Complete Years", "Start Year", "End Year"])

for basinID, completeYears in completeBasins_Chile.items():
    csvDict = {}
    csvDict["ID"] = basinID
    csvDict["Source"] = "Chile"
    csvDict["No Complete Years"] = completeYears.shape[0]
    csvDict["Start Year"] = completeYears.index[0]
    csvDict["End Year"] = completeYears.index[-1]
    csvDF = csvDF.append(csvDict, ignore_index = True)
    
    
for basinID, completeYears in completeBasins_GHCND_SA.items():
    csvDict = {}
    csvDict["ID"] = basinID[:-4]
    csvDict["Source"] = "GHCND_SA"
    csvDict["No Complete Years"] = completeYears.shape[0]
    csvDict["Start Year"] = completeYears["year"].min()
    csvDict["End Year"] = completeYears["year"].max()
    csvDF = csvDF.append(csvDict, ignore_index = True)
    
csvDF.to_csv(os.path.join(root,"Complete Basins.csv"), line_terminator = '\r')
csvDF.to_csv()