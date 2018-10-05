# -*- coding: utf-8 -*-
"""
Generates a bunch of equidistant lat/lon coordinate points within an urban
area, and uses the Google maps API to compute the travel distance between them.

@author: nequals30 (http://www.nequals30.com)
"""

#%% Imports
# --------------------------------------------------------
import shapefile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import path
import urllib.request
import json

#%% Overall Settings
# --------------------------------------------------------
ptResolution = 5

#%% Generate a big dataframe of all urban area boundaries
# --------------------------------------------------------
# Downloaded from here (unzip the contents into that folder, you will need
# all the contents):
# https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html
# This will work with metro areas, urban areas, etc.

shp = shapefile.Reader('cb_2017_us_county_500k/cb_2017_us_county_500k.shp')
fields = [x[0] for x in shp.fields][1:]
records = shp.records()
shps = [s.points for s in shp.shapes()]
allAreas = pd.DataFrame(columns=fields, data=records)

#%% Get outline for this specific county
# --------------------------------------------------------
# how do I do a matlab find()? This seems like not the right way to do it:
outline = shps[np.where(allAreas.GEOID.astype(str)=='29510')[0][0]]
path_out = path.Path(outline)
x_out, y_out = zip(*outline)

# Generate coordinates inside the outline
x_pts,y_pts = np.meshgrid(np.linspace(min(x_out),max(x_out),num=ptResolution),np.linspace(min(y_out),max(y_out),num=ptResolution))
x_pts = x_pts.flatten()
y_pts = y_pts.flatten()

# Remove points outside the outline
isInside = path_out.contains_points(np.vstack((x_pts,y_pts)).T)
x_pts = x_pts[isInside]
y_pts = y_pts[isInside]

# Plot the results
plt.plot(x_out,y_out)
plt.scatter(x_pts,y_pts)
#plt.axis([-90.5, -90, 38.5, 39])
plt.show()


#%% Get Distance Matrix from Bing API
xy_pairs = zip(y_pts,x_pts)
coordString = str(xy_pairs).strip('[]')

try:
    pd.read_csv('yo.csv')
except IOError:
# Request distance matrix from API --------------------------------------------
    credentials = open('bing_credentials.config','r')
    apiKey = credentials.readlines()[0].strip()
    credentials.close()
    theUrl = "https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins=38.5926,-90.2820&destinations=38.7138,-90.2435&travelMode=driving&key=" + apiKey
    
    request = urllib.request.Request(theUrl)
    response = urllib.request.urlopen(request)
    
    r = response.read().decode(encoding="utf-8")
    result = json.loads(r)
    
    print(result["resourceSets"][0]["resources"][0]["results"][0]["travelDuration"])

print("end of analysis")