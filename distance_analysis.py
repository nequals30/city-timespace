# -*- coding: utf-8 -*-
"""
Generates a bunch of equidistant lat/lon coordinate points within a US county, 
then uses the Bing Distance Matrix API to get the distances between them.

Then it uses multi-dimensional scaling (MDS) to re-map the coordinates in
time-space.


@author: Alik Ulmasov (http://www.nequals30.com)
"""

#%% Imports
# --------------------------------------------------------
import shapefile

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import path
from sklearn import manifold

import urllib.request
import json

#%% Settings
# --------------------------------------------------------
apiKey = "" # Your Bing API key goes here
ptResolution = 5


#%% Generate a big dataframe of all county boundaries
# --------------------------------------------------------
# Downloaded from here:
# https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html

# Unzip the contents in this directory, you will need  all the contents
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


#%% Get Distance Matrix from Bing API
# --------------------------------------------------------

try:
    tempLoad = open('tempResults.txt','r')
    result = json.load(tempLoad)
    tempLoad.close()
except IOError:
    # My API key is stored in a seperate file ---------------------------------
    if not apiKey:
        credentials = open('bing_credentials.config','r')
        apiKey = credentials.readlines()[0].strip()
        credentials.close()
    
    # Construct the URL
    latLon = ''
    for i in range(len(y_pts)):
        latLon += "{0:.4f},{1:.4f};".format(y_pts[i],x_pts[i])
    latLon = latLon[:-1]
        
    theUrl = ("https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?" +
              "origins=" + latLon +
              "&destinations=" + latLon + 
              "&travelMode=driving&key=" + apiKey )
    
    # Request distance matrix from API ----------------------------------------
    request = urllib.request.Request(theUrl)
    response = urllib.request.urlopen(request)
    
    r = response.read().decode(encoding="utf-8")
    result = json.loads(r)
    
    # Save off the result (so as not to call it again) ------------------------
    tempSave = open('tempResults.txt','w')
    json.dump(result,tempSave)
    tempSave.close()


#%% Turn results into distance matrix
# --------------------------------------------------------
dmDict = result["resourceSets"][0]["resources"][0]["results"]

origIdx = [x['originIndex'] for x in dmDict]
destIdx = [x['destinationIndex'] for x in dmDict]
dur = [x['travelDuration'] for x in dmDict]

distMat = np.zeros((len(y_pts),len(x_pts)))
distMat[origIdx,destIdx] = dur


#%% Do Prinicpal Coordinates Analysis on the distance matrix
# --------------------------------------------------------
mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=2)
coords = mds.fit(distMat).embedding_


#%% Final Plotting
# --------------------------------------------------------
f, (ax1, ax2) = plt.subplots(1, 2)

ax1.plot(x_out,y_out)
ax1.scatter(x_pts,y_pts)
for i in list(range(len(x_pts))):
    ax1.annotate(str(i),(x_pts[i],y_pts[i]))

ax2.scatter(coords[:, 0], coords[:, 1], marker = 'o')
for i in list(range(len(x_pts))):
    ax2.annotate(str(i),(coords[i,0],coords[i,1]))
plt.show()


print("end of analysis")