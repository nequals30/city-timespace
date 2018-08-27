#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Generates a bunch of equidistant lat/lon coordinate points within an urban
area, and uses the Google maps API to compute the travel distance between them.

@author: nequals30 (http://www.nequals30.com)
"""

import shapefile
import pandas as pd
import googlemaps

# Generate a big dataframe of all urban area boundaries -----------------------

shp = shapefile.Reader('cb_2017_us_ua10_500k/cb_2017_us_ua10_500k.shp')

fields = [x[0] for x in shp.fields][1:]
records = shp.records()
shps = [s.points for s in shp.shapes()]
allUrbanAreas = pd.DataFrame(columns=fields, data=records)
allUrbanAreas = allUrbanAreas.assign(coords=shps)    


# Generate the coordinates for our area ---------------------------------------

thisPolygon = allUrbanAreas.coords[allUrbanAreas.NAME10=='St. Louis, MO--IL']

# figure out bounding box
# figure out points


# Get API key from config file ------------------------------------------------
credentials = open('googlemaps_credentials.config','r')
apiKey = credentials.readlines()[0].strip()
credentials.close()


# Connect to Google Maps API
#gm = googlemaps.Client(key=apiKey)

# gOut = gm.distance_matrix('Nashville','Austin', units='metric')

