# get_noaa_ghcn_data

Global Historical Climatology Network data parsed into reshaped CSVs. The `get_dly.py` program grabs a .dly file from the NOAA GHCN FTP server, parses, and reshapes to have one day per row and element values in the columns. The output is written out as a pandas DataFrame and a CSV file.

Data source: https://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/global-historical-climatology-network-ghcn

 
```
.dly Format In (roughly):                     .csv Format Out (roughly):
-------------------------                     --------------------------
Month1  PRCP  Day1  Day2 ... Day31            Day1  PRCP  SNOW
Month1  SNOW  Day1  Day2 ... Day31            Day2  PRCP  SNOW
Month2  PRCP  Day1  Day2 ... Day31            Day3  PRCP  SNOW
Month2  SNOW  Day1  Day2 ... Day31            Day4  PRCP  SNOW
```

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
    
[Codebook/ICD](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt):

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



## FIXME
* Focus on .dly first
  * ~~Grab current .dly file from FTP server~~
    * ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/
  * ~~Read .dly file into DataFrame using ICD~~
    * https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
    * ~~Create separate lists first then create empty DataFrame and fill with lists as columns~~
  * Option to download .dly file or read from stream?
  * ~~Reshape data to have one day per line (lump flags together like Q-XY)~~
  
    | DAY | PRCP | PRCP_M | PRCP_Q | PRCP_S | TMIN | TMIN_M | ... |
    | --- | ---- | ------ | ------ | ------ | ---- | ------ | --- |
    | 12  | 0.5  | X      | X      |  X     | 55   | X      | ... |
    
    OR
    
    | DAY | PRCP | PRCP_FLAGS | TMIN | TMIN_FLAGS | ... |
    | --- | ---- | ---------- | ---- | ---------- | --- |
    | 12  | 0.5  | Q-XY       | 55   | MX-        | ... |
    
  * ~~Ouput file as CSV~~
* ~~Make search tool to get station IDs~~
  * ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
* Import reshaped files into database instead of CSVs
* Make awesome charts!
