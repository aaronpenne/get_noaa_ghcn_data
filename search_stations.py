# -*- coding: utf-8 -*-
"""
Searches list of stations via user input to find the station ID.

Author: Aaron Penne

------------------------------
Variable   Columns   Type
------------------------------
ID            1-11   Character
LATITUDE     13-20   Real
LONGITUDE    22-30   Real
ELEVATION    32-37   Real
STATE        39-40   Character
NAME         42-71   Character
GSN FLAG     73-75   Character
HCN/CRN FLAG 77-79   Character
WMO ID       81-85   Character
------------------------------


"""

import pandas as pd
from ftplib import FTP
import os

output_dir = os.path.relpath('output')
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

ftp_path_dly = '/pub/data/ghcn/daily/'
ftp_path_dly_all = '/pub/data/ghcn/daily/all/'
ftp_filename = 'ghcnd-stations.txt'

def connect_to_ftp():
    # Get FTP server and file details
    ftp_path_root = 'ftp.ncdc.noaa.gov'
    
    # Access NOAA FTP server
    ftp = FTP(ftp_path_root)
    message = ftp.login()  # No credentials needed
    print(message)
    return ftp

def get_station_id(ftp):    
    # Get stations file
    ftp_full_path = os.path.join(ftp_path_dly, ftp_filename)
    local_full_path = os.path.join(output_dir, ftp_filename)
    if not os.path.isfile(local_full_path):
        with open(local_full_path, 'wb+') as f:
            ftp.retrbinary('RETR ' + ftp_full_path, f.write)
            
    # Get user search term
    print()
    query = input('Enter station name, full or partial. (ex. Washington, san fran, USC): ')
    query = query.upper()
    # FIXME try/catch and clean input
    print()
    
    # Read stations text file using fixed-width-file reader built into pandas
    # http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_fwf.html
    dtype = {'STATION_ID': str,
             'LATITUDE': float,
             'LONGITUDE': float,
             'ELEVATION': float,
             'STATE': str,
             'STATION_NAME': str,
             'GSN_FLAG': str,
             'HCN_CRN_FLAG': str,
             'WMO_ID': str}
    names = list(dtype.keys())
    widths = [11,  # Station ID
              9,   # Latitude (decimal degrees)
              10,  # Longitude (decimal degrees)
              7,   # Elevation (meters)
              3,   # State (USA stations only)
              31,  # Station Name
              4,   # GSN Flag
              4,   # HCN/CRN Flag
              6]   # WMO ID
    df = pd.read_fwf(local_full_path, widths=widths, names=names, dtype=dtype, header=None)
    
    # Replace missing values (nan, -999.9)
    df['STATE'] = df['STATE'].replace('nan', '--')
    df['GSN_FLAG'] = df['GSN_FLAG'].replace('nan', '---')
    df['HCN_CRN_FLAG'] = df['GSN_FLAG'].replace('nan', '---')
    df = df.replace(-999.9, float('nan'))
    
    # Get query results, but only the columns we care about
    print('Searching records...')
    matches = df['STATION_NAME'].str.contains(query)
    df = df.loc[matches, ['STATION_ID', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'STATE', 'STATION_NAME']]
    df.reset_index(drop=True, inplace=True)
    
    # Get file sizes of each station's records to augment results
    print('Getting file sizes...', end='')
    ftp.voidcmd('TYPE I')  # Needed to avoid FTP error with ftp.size()
    for i in list(df.index):
        print('.', end='')
        ftp_dly_file = ftp_path_dly + 'all/' + df.loc[i, 'STATION_ID'] + '.dly'
        df.loc[i, 'SIZE'] = round(ftp.size(ftp_dly_file)/1000)  # Kilobytes
    print()
    print()
    
    # Sort by size then by rounded lat/long values to group geographic areas and show stations with most data
    df_sort = df.round(0)
    df_sort.sort_values(['LATITUDE', 'LONGITUDE', 'SIZE'], ascending=False, inplace=True)
    df = df.loc[df_sort.index]
    df.reset_index(drop=True, inplace=True)
    
    # Print headers to facilitate reading
    selection = 'Index'
    station_id = 'Station_ID '
    lat = 'Latitude'
    lon = 'Longitude'
    state = 'State'
    name = 'Station_Name                '
    size = ' File_Size'
    # Format output to be pretty, hopefully there is a prettier way to do this.
    print('{: <6}{: <31}{: <6}({: >8},{: >10}){: >13}'.format(selection, name, state, lat, lon, size))
    print('-'*5 + ' ' + '-'*30 + ' ' + '-'*5 + ' ' + '-'*21 + ' ' + '-'*12)
    for i in list(df.index):
        print('{: 4}: {: <31}{: <6}({:8.4f},{:10.4f}){:10.0f} Kb'.format(i,
                                                                          df.loc[i,'STATION_NAME'],
                                                                          df.loc[i,'STATE'],
                                                                          df.loc[i,'LATITUDE'],
                                                                          df.loc[i,'LONGITUDE'],
                                                                          df.loc[i,'SIZE']))
    
    # Get user selection
    query = input('Enter selection (ex. 001, 42): ')
    query = int(query)
    # FIXME try/catch and clean input
    
    station_id = df.loc[query, 'STATION_ID']
    return station_id

if __name__ == '__main__':
    ftp = connect_to_ftp()
    station_id = get_station_id(ftp)
    print(station_id)
    ftp.quit()