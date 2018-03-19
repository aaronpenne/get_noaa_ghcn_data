# -*- coding: utf-8 -*-
"""
Driver script to interface with NOAA GHCN FTP server, search for station data
with plain English text, and download station data in a reformatted easy-to-read CSV

Author: Aaron Penne
Created: 2018-03-16

"""

import get_station_id
import get_dly


if __name__ == '__main__':
    ftp = get_station_id.connect_to_ftp()
    station_id = get_station_id.get_station_id(ftp)
    get_dly.dly_to_csv(ftp, station_id)
    ftp.quit()
