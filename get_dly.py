# -*- coding: utf-8 -*-
"""
Grabs .dly file from the NOAA GHCN FTP server, parses, and reshapes to have one 
day per row and element values in the columns. Writes output as CSV.

Author: Aaron Penne
 

.dly Format In (roughly):                     .csv Format Out (roughly):
-------------------------                     --------------------------
Month1  PRCP  Day1  Day2 ... Day31            Day1  PRCP  SNOW
Month1  SNOW  Day1  Day2 ... Day31            Day2  PRCP  SNOW
Month2  PRCP  Day1  Day2 ... Day31            Day3  PRCP  SNOW
Month2  SNOW  Day1  Day2 ... Day31            Day4  PRCP  SNOW


Starting with 5 core elements (per README)
    PRCP = Precipitation (tenths of mm)
    SNOW = Snowfall (mm)
    SNWD = Snow depth (mm)
    TMAX = Maximum temperature (tenths of degrees C)
    TMIN = Minimum temperature (tenths of degrees C)

Conversions:
    PRCP = (tenths of mm) -> (mm)
    TMAX = (tenths of degrees C) -> (degrees C)
    TMIN = (tenths of degrees C) -> (degrees C)
    
ICD:
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
"""

import pandas as pd
from ftplib import FTP
from io import StringIO
import os

output_dir = 'C:\\tmp\\noaa_ghcn\\'
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

# Get FTP server and file details
ftp_path_root = 'ftp.ncdc.noaa.gov'
ftp_path_dly = '/pub/data/ghcn/daily/all/'
# FIXME this will become the result of a search on the stations txt file
ftp_filename = 'USW00093134.dly'  # USW00093134  34.0511 -118.2353   70.1 CA LOS ANGELES DWTN USC CAMPUS 

# Access NOAA FTP server
ftp = FTP(ftp_path_root)
ftp.login()  # No credentials needed

# Write .dly file to stream using StringIO using FTP command 'RETR'
s = StringIO()
ftp.retrlines('RETR ' + ftp_path_dly + ftp_filename, s.write)

def create_dict(element):
    element = element.upper()
    dict_element = {'ID': [],
                    'YEAR': [],
                    'MONTH': [],
                    'DAY': [],
                    element : [],
                    element + '_FLAGS': []}
    return dict_element

# Get flags, replacing empty flags with '-' for clarity (' S ' becomes '-S-')
def get_flags():
    m_flag = s.read(1)
    m_flag = m_flag if m_flag.strip() else '-'
    q_flag = s.read(1)
    q_flag = q_flag if q_flag.strip() else '-'
    s_flag = s.read(1)
    s_flag = s_flag if s_flag.strip() else '-'
    return [m_flag + q_flag + s_flag]

# https://docs.python.org/3/tutorial/controlflow.html#unpacking-argument-lists
def get_day(element, **dict_element):
    element = element.upper()
    dict_element['ID'] += [id_station]  # Write metadata for current day
    dict_element['YEAR'] += [year]
    dict_element['MONTH'] += [month]
    dict_element['DAY'] += [str(day)]
    dict_element[element] += [s.read(5)]  # Get current value
    dict_element[element + '_FLAGS'] += get_flags()  # Aggregate flags
    return dict_element

# Make dataframes out of the dicts, make the indices date strings (YYYY-MM-DD)
def create_dataframe(element, dict_element):
    element = element.upper()
    df_element = pd.DataFrame(dict_element)
    # Add dates (YYYY-MM-DD) as index on df. Pad days with zeros to two places
    df_element.index = df_element['YEAR'] + '-' + df_element['MONTH'] + '-' + df_element['DAY'].str.zfill(2)
    df_element.index.name = 'DATE'
    # Add ID as secondary (primary?) index on df
    df_element = pd.concat([df_element], keys=df_element['ID'])
    # Clean up df, convert rows that have no values (-9999) to NaN
    df_element = df_element.replace('-9999', float('nan'))
    # Arrange columns so ID, YEAR, MONTH, DAY are at front. Leaving them in for plotting later - https://stackoverflow.com/a/31396042
    for col in ['DAY', 'MONTH', 'YEAR', 'ID']:
        df_element = move_col_to_front(col, df_element)
    # Convert numerical values to float
    df_element.loc[:,element] = df_element.loc[:,element].astype(float)
    return df_element
    
def move_col_to_front(element, df):
    element = element.upper()
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index(element)))
    df = df.reindex(columns=cols)
    return df
    
# Move to first char in file
s.seek(0)

# Create empty dictionaries for each element. 
# FIXME Surely there is a better way to do this.
prcp = create_dict('PRCP')
snow = create_dict('SNOW')
snwd = create_dict('SNWD')
tmax = create_dict('TMAX')
tmin = create_dict('TMIN')

num_chars_line = 269
num_chars_metadata = 21

# Read through entire StringIO stream (the .dly file) and collect the data
i = 0
while True:
    i += 1
    
    # Read metadata for each line (one month of data for a particular element per line)
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
    
    # Loop through each day in rest of row, break if current position is end of row
    while True:
        day += 1
        # Fill in contents of each dict depending on element type in current row
        if element == 'PRCP':
            prcp = get_day(element, **prcp)
        elif element == 'SNOW':
            snow = get_day(element, **snow)
        elif element == 'SNWD':
            snwd = get_day(element, **snwd)
        elif element == 'TMAX':
            tmax = get_day(element, **tmax)
        elif element == 'TMIN':
            tmin = get_day(element, **tmin)
        else:
            # If we don't care about the element, skip the row
            ignored_row = s.read(num_chars_line-num_chars_metadata) 
        
        # Stop reading row if we reached the end of it
        if s.tell() % num_chars_line == 0:
            break
        
# Create dataframes from dict
df_prcp = create_dataframe('PRCP', prcp)
df_snow = create_dataframe('SNOW', snow)
df_snwd = create_dataframe('SNWD', snwd)
df_tmax = create_dataframe('TMAX', tmax)
df_tmin = create_dataframe('TMIN', tmin)

# Combine all element dataframes into one dataframe, indexed on date. 
# pd.concat automagically aligns values to matching indices, therefore the data is date aligned!
list_dfs = [df_prcp,
            df_snow,
            df_snwd,
            df_tmax,
            df_tmin]
df_all = pd.concat(list_dfs, axis=1)

# Remove duplicated columns - https://stackoverflow.com/a/40435354
df_all = df_all.loc[:,~df_all.columns.duplicated()]

# Calculate average temperature since min/max are given
df_all['TAVG_CALC'] = (df_all['TMAX'] + df_all['TMIN']) / 2

# Convert to base units (doing this after TAVG_CALC gets rid of large float decimals in CSV)
df_all['PRCP'] = df_all['PRCP'] / 10
df_all['TMAX'] = df_all['TMAX'] / 10
df_all['TMIN'] = df_all['TMIN'] / 10
df_all['TAVG_CALC'] = df_all['TAVG_CALC'] / 10

# Output to CSV, convert everything to strings first
# NOTE: To open the CSV in Excel, go through the CSV import wizard, otherwise it will come out broken
df_out = df_all.astype(str)
df_out.to_csv(output_dir + ftp_filename + '.csv')


##############################################################################
# Ploting needs to get moved to different file

import seaborn as sns
import matplotlib.pyplot as plt

# Filter data to years with complete records (1921 to 2017 after doing
# inspection with df.pivot_table(values='TMAX', columns='YEAR', aggfunc='count'))
year_filter = [str(i) for i in range(1921,2017)]
df = df_all.loc[df_all['YEAR'].isin(year_filter)]
bandwidth = 0.35

# Set up plotting and formatting of viz
sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
font_h1 = {'family': 'monospace',
           'color': 'black',
           'weight': 'bold',
           'size': 16,
           'horizontalalignment': 'center'}
font_h2 = {'family': 'monospace',
           'color': 'black',
           'size': 14,
           'horizontalalignment': 'center'}
font_sub = {'family': 'monospace',
            'color': 'black',
            'weight': 'regular',
            'size': 10,
            'horizontalalignment': 'right'}

# Create axes for each Year, one row per Year
g = sns.FacetGrid(data=df,
                  row='YEAR',  # Determines which value to group by, in this case the different values in the 'Year' column
                  hue='YEAR',  # Similar to row. Enables the date labels on each subplot
                  aspect=18,   # Controls aspect ratio of entire figure
                  size=0.5,    # Controls vertical height of each subplot
                  palette=sns.color_palette("Set2", 1))  # Uses a nice green for the area

# Create KDE area plots
#g.map(sns.kdeplot, 'TMAX', bw=bandwidth, clip_on=False, shade=True, alpha=1)

# Create KDE line plots to outline the areas
g.map(sns.kdeplot, 'TMAX', bw=bandwidth, clip_on=False, color='black')

# Create the psuedo x-axes
#g.map(plt.axhline, y=0, lw=2, clip_on=False, color='black')

# Define and use a simple function to label the plot in axes coordinates
# https://seaborn.pydata.org/examples/kde_joyplot.html
def label(x, color, label):
    ax = plt.gca()
#    ax.set_xlim([-2,4])
    ax.text(0, 0.07, 
            label,
            family='monospace',
            fontsize=12,
            color='black', 
            ha='left',
            va='center',
            transform=ax.transAxes)
g.map(label, 'TMAX')

# Overlap the plots to give the ridgeline effect
g.fig.subplots_adjust(hspace=-.9)

# Clean up axes and remove subplot titles
g.set_titles('')
g.set(yticks=[])
#plt.xticks([0, 1, 2, 3], 
#           ['Constitutional Ban',
#            'Statutory Ban',
#            'No Law',
#            'Legal'],
#            rotation=90,
#            fontsize=12,
#            fontname='monospace')
plt.xlabel('')
g.despine(bottom=True, left=True)

# Add titles and annotations
#plt.text(1, 8.5,
#         'State Same Sex Marriage Laws in the USA',
#         fontdict=font_h1)
#plt.text(1, 8.3,
#         'Percent of states w/each law type from 1995-2015',
#         fontdict=font_h2)
#plt.text(4, -1.8,
#         '© Aaron Penne 2018\nSource: Pew Research Center',
#         fontdict=font_sub)

g.savefig('{0}joy_TMAX.png'.format(output_dir), dpi=300, bbox_inches='tight')