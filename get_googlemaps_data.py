#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Generates a bunch of equidistant lat/lon coordinate points within an urban
area, and uses the Google maps API to compute the travel distance between them.

@author: nequals30 (http://www.nequals30.com)
"""

import shapefile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import path
import googlemaps

# Generate a big dataframe of all urban area boundaries -----------------------

# Downloaded from here (unzip the contents into that folder, you will need
# all the contents):
# https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html
# This will work with metro areas, urban areas, etc.

shp = shapefile.Reader('cb_2017_us_county_500k/cb_2017_us_county_500k.shp')
fields = [x[0] for x in shp.fields][1:]
records = shp.records()
shps = [s.points for s in shp.shapes()]
allAreas = pd.DataFrame(columns=fields, data=records)

# Generate the coordinates for our area ---------------------------------------

# how do I do a matlab find()? This seems like not the right way to do it:
outline = shps[np.where(allAreas.GEOID.astype(str)=='29510')[0][0]]
path_out = path.Path(outline)
x_out, y_out = zip(*outline)

x_pts,y_pts = np.meshgrid(np.linspace(min(x_out),max(x_out),num=25),np.linspace(min(y_out),max(y_out),num=25))
x_pts = x_pts.flatten()
y_pts = y_pts.flatten()
isInside = path_out.contains_points(np.vstack((x_pts,y_pts)).T)

# Optional: Plot the results
plt.plot(x_out,y_out)
plt.scatter(x_pts[isInside],y_pts[isInside])
plt.show()

# Get API key from config file ------------------------------------------------

credentials = open('googlemaps_credentials.config','r')
apiKey = credentials.readlines()[0].strip()
credentials.close()

# Connect to Google Maps API --------------------------------------------------

#gm = googlemaps.Client(key=apiKey)
# gOut = gm.distance_matrix('Nashville','Austin', units='metric')
# nested for loop through all points, save to pd series
# save as csv
