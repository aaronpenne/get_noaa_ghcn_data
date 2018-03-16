# -*- coding: utf-8 -*-
"""
Driver script to interface with NOAA GHCN FTP server, search for station data
with plain English text, download station data in a reformatted easy-to-read CSV

Author: Aaron Penne
Created: 2018-03-16

"""

import search_stations
import get_dly

ftp = search_stations.connect_to_ftp()
station_id = search_stations.get_station_id(ftp)
get_dly.dly_to_csv(ftp, station_id)
ftp.quit()
