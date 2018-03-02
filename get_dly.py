# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 08:20:52 2018

@author: 596192

Starting with 5 core elements (per README)
    PRCP = Precipitation (tenths of mm)
    SNOW = Snowfall (mm)
    SNWD = Snow depth (mm)
    TMAX = Maximum temperature (tenths of degrees C)
    TMIN = Minimum temperature (tenths of degrees C)
   
Format In:
    ------------------------------
    Variable   Columns   Type
    ------------------------------
    ID            1-11   Character
    YEAR         12-15   Integer
    MONTH        16-17   Integer
    ELEMENT      18-21   Character
    VALUE1       22-26   Integer
    MFLAG1       27-27   Character
    QFLAG1       28-28   Character
    SFLAG1       29-29   Character
    VALUE2       30-34   Integer
    MFLAG2       35-35   Character
    QFLAG2       36-36   Character
    SFLAG2       37-37   Character
      .           .          .
      .           .          .
      .           .          .
    VALUE31    262-266   Integer
    MFLAG31    267-267   Character
    QFLAG31    268-268   Character
    SFLAG31    269-269   Character
    ------------------------------

Format Out:
    |  PRCP  |  PRCP_FLAGS  |  TMIN  |  TMIN_FLAGS  |  ...
"""

import pandas as pd
import matplotlib.pyplot as plt
from ftplib import FTP
from io import StringIO

ftp_path_root = 'ftp.ncdc.noaa.gov'
ftp_path_dly = '/pub/data/ghcn/daily/all/'
ftp_file_name = 'USW00093134.dly'  # USW00093134  34.0511 -118.2353   70.1 CA LOS ANGELES DWTN USC CAMPUS 

ftp = FTP(ftp_path_root)
ftp.login()  # No credentials needed
s = StringIO()
ftp.retrlines('RETR ' + ftp_path_dly + ftp_file_name, s.write)


# Get flags, replacing empty flags with '-' for clarity (' S ' becomes '-S-')
def get_flags():
    m_flag = s.read(1)
    m_flag = m_flag if m_flag.strip() else '-'
    q_flag = s.read(1)
    q_flag = q_flag if q_flag.strip() else '-'
    s_flag = s.read(1)
    s_flag = s_flag if s_flag.strip() else '-'
    return [m_flag + q_flag + s_flag]


s.seek(0)  # Move to first char in file

prcp = {'ID': [],
        'YEAR': [],
        'MONTH': [],
        'DAY': [],
        'PRCP': [],
        'PRCP_FLAGS': []}
snow = {'ID': [],
        'YEAR': [],
        'MONTH': [],
        'DAY': [],
        'SNOW': [],
        'SNOW_FLAGS': []}
snwd = {'ID': [],
        'YEAR': [],
        'MONTH': [],
        'DAY': [],
        'SNWD': [],
        'SNWD_FLAGS': []}
tmax = {'ID': [],
        'YEAR': [],
        'MONTH': [],
        'DAY': [],
        'TMAX': [],
        'TMAX_FLAGS': []}
tmin = {'ID': [],
        'YEAR': [],
        'MONTH': [],
        'DAY': [],
        'TMIN': [],
        'TMIN_FLAGS': []}

num_chars_line = 269
num_chars_metadata = 21

i = 0
while True:
    i += 1
    id_station = s.read(11)
    year = s.read(4)
    month = s.read(2)
    day = 0
    element = s.read(4)
    
    # If this is blank then we've reached EOF and should exit loop
    if not element:
        break
    
    # Let us know if it's running
    print('{}-{}  {}'.format(year, month, i))
    
    # Loop through each value in rest of row, break if current position is end of row
    while True:
        day += 1
        # Fill in contents of each dict depending on element type in current row
        if element == 'PRCP':
            prcp['ID'] += [id_station]  # Write metadata for current day
            prcp['YEAR'] += [year]
            prcp['MONTH'] += [month]
            prcp['DAY'] += [str(day)]
            prcp['PRCP'] += [s.read(5)]  # Get current value
            prcp['PRCP_FLAGS'] += get_flags()  # Aggregate flags
            
        elif element == 'SNOW':
            snow['ID'] += [id_station]  # Write metadata for current day
            snow['YEAR'] += [year]
            snow['MONTH'] += [month]
            snow['DAY'] += [str(day)]
            snow['SNOW'] += [s.read(5)]  # Get current value
            snow['SNOW_FLAGS'] += get_flags()  # Aggregate flags
            
        elif element == 'SNWD':
            snwd['ID'] += [id_station]  # Write metadata for current day
            snwd['YEAR'] += [year]
            snwd['MONTH'] += [month]
            snwd['DAY'] += [str(day)]
            snwd['SNWD'] += [s.read(5)]  # Get current value
            snwd['SNWD_FLAGS'] += get_flags()  # Aggregate flags
            
        elif element == 'TMAX':
            tmax['ID'] += [id_station]  # Write metadata for current day
            tmax['YEAR'] += [year]
            tmax['MONTH'] += [month]
            tmax['DAY'] += [str(day)]
            tmax['TMAX'] += [s.read(5)]  # Get current value
            tmax['TMAX_FLAGS'] += get_flags()  # Aggregate flags
      
        elif element == 'TMIN':
            tmin['ID'] += [id_station]  # Write metadata for current day
            tmin['YEAR'] += [year]
            tmin['MONTH'] += [month]
            tmin['DAY'] += [str(day)]
            tmin['TMIN'] += [s.read(5)]  # Get current value
            tmin['TMIN_FLAGS'] += get_flags()  # Aggregate flags
            
        else:
            ignored_row = s.read(num_chars_line-num_chars_metadata) # Skip to next row of records
        
        # Stop reading row if we reached the end of it
        if s.tell() % num_chars_line == 0:
            break
