#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 10:33:53 2022

@author: yihan
"""

import pandas as pd
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import itertools
from geopy.distance import geodesic
from datetime import datetime


class collocated:
    
    def __init__(self):
        
        # Chinese territory
        self.cmaxlat = 53.5
        self.cminlat = 4
        self.cmaxlon = 135
        self.cminlon = 73.5
                
        
    def select_geoinfo(self, sensorname: str, path: str, filename: str) -> pd.DataFrame:
        
        # select parameter name
        if(sensorname == 'AHI'):
            lat_grid = 'grid_yt'
            lon_grid = 'grid_xt'   
            
        elif(sensorname == 'GDAS'):
            lat_grid = 'lat_0'
            lon_grid = 'lon_0'
        
        # Read in sensor geographical information
        ds = nc.Dataset(path + filename)
        
        lon_grid = ds[lon_grid][:]
        lat_grid = ds[lat_grid][:]
           
        # keep geographical information and position information into dataframe 
        # dataframe will help us collocate values in two sensors easily
        sensor_geo = []
        sensor_index = []

        for geo in itertools.product(lat_grid,lon_grid):
            sensor_geo.append(geo)
    
        for index in itertools.product(list(range(len(lat_grid))),list(range(len(lon_grid)))):
            sensor_index.append(index)

        # store four columns in dataframe
        # lat, lon, (lat, lon), (IDX, IDY)
        df_sensor_geo = pd.DataFrame(sensor_geo, columns=['lat','lon'])

        df_sensor_geo['lat_lon'] = sensor_geo
        df_sensor_geo['IDX_IDY'] = sensor_index
        
        return df_sensor_geo
 
    
    
    def match_geoinfo(self, df_low_res: pd.DataFrame, df_high_res: pd.DataFrame, territory_limit: str) -> pd.DataFrame:
        
        # the collocated data we need is only China area
        if(territory_limit == 'China'):
            c_max_lat = self.cmaxlat
            c_min_lat = self.cminlat
            c_max_lon = self.cmaxlon
            c_min_lon = self.cminlon 
        
            # only select China area, which will improve effeciency
            df_low_res = df_low_res[(df_low_res['lat'] > c_min_lat)\
                                   &(df_low_res['lat'] < c_max_lat)\
                                   &(df_low_res['lon'] < c_max_lon)\
                                   &(df_low_res['lon'] > c_min_lon)]
        
            
        def find_nearest(df: pd.DataFrame):
            geo = df['lat_lon']
            print(geo)
            max_lat, max_lon, min_lat, min_lon = geo[0]+1, geo[1]+1, geo[0]-1, geo[1]-1
   
            df_selected = df_high_res[(df_high_res['lat'] > min_lat)\
                                     &(df_high_res['lat'] < max_lat)\
                                     &(df_high_res['lon'] < max_lon)\
                                     &(df_high_res['lon'] > min_lon)]
      
            distance = df_selected['lat_lon'].apply(lambda x: geodesic(x, geo).km)

            lat_lon = df_high_res.loc[distance.idxmin(), 'lat_lon']
            IDX_IDY = df_high_res.loc[distance.idxmin(), 'IDX_IDY']
   
            return lat_lon, IDX_IDY
                
        df_low_res[['high_lat_lon','high_IDX_IDY']] = df_low_res.apply(find_nearest, axis=1, result_type ='expand')   
     
        return df_low_res
        
        
        


def main():
    
    #### files Information ####
    AHI_path = './AHI/'
    AHI_filename = 'gfs.t00z.sfcf001.nc'
    GDAS_path = './GDAS/'
    GDAS_filename = 'gdas1.fnl0p25.2022071912.f09.grib2.nc'
    
    ### Read sensors information into dataframe format
    df_AHI_geo = collocated().select_geoinfo('AHI', AHI_path, AHI_filename)
    df_GDAS_geo = collocated().select_geoinfo('GDAS', GDAS_path, GDAS_filename)
    
    
    ### Collocate two sensors' geographical information in China area
    df_collocated = collocated().match_geoinfo(df_GDAS_geo, df_AHI_geo, 'China')
    
    
    return df_collocated

if __name__ =='__main__':
    
    start=datetime.now()
    print('start time', start)
    
    df_collocated = main()      
    
    #Statements
    end = datetime.now()

    print('This code cost time:', end-start)
            
     
