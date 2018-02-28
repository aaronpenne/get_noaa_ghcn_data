# noaa_ghcn_data_to_csv
Global Historical Climatology Network data parsed into reshaped CSVs


## FIXME
* Focus on .dly first
  * Grab current .dly file from FTP server
    * ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/
  * Read .dly file into DataFrame using ICD
    * https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
  * Reshape data to have one day per line
  
    | DAY | PRCP | PRCP_M | PRCP_Q | PRCP_S | TMIN | TMIN_M | ... |
    | --- | ---- | ------ | ------ | ------ | ---- | ------ | --- |
    | 12  | 0.5  | X      | X      |  X     | 55   | X      | ... |
    
  * Ouput file as CSV
* Make search tool to get station IDs
  * ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
* Import reshaped files into database instead of CSVs
* Make awesome charts!
