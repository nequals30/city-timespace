#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Generates a bunch of points to represent the city

@author: nequals30 (http://www.nequals30.com)
"""

import shapefile
import googlemaps

# Import urban area boundary (source from census)
shp = shapefile.Reader('cb_2017_us_ua10_500k.shp')

#X = shp.shapeRecords()[0].record[3]
for i in range(1,len(shp.shapeRecords())):
     print(shp.shapeRecords()[i].record[3])

# Generate points within area bounding box

# Get API key from config file 
credentials = open('googlemaps_credentials.config','r')
apiKey = credentials.readlines()[0].strip()
credentials.close()

# Connect to Google Maps API
#gm = googlemaps.Client(key=apiKey)

# gOut = gm.distance_matrix('Nashville','Austin', units='metric')

print("yo")