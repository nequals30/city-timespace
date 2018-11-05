# -*- coding: utf-8 -*-
"""
Generates equidistant lat/lon coordinate points within a set of US counties, 
then uses the Bing Distance Matrix API to get the distances between them.

Then it uses multi-dimensional scaling (MDS) to re-map the coordinates in
time-space, and plots the results.

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
from sklearn.decomposition import PCA

import urllib.request
import json

#%% Settings
# --------------------------------------------------------
apiKey = "" # Your Bing API key goes here
ptResolution = 11

countyGEOIDs = ['29510','29189'] #st. louis city and county

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

#%% Get outline for your specific counties and generate points
# --------------------------------------------------------
idxShapes = np.where(np.isin(allAreas['GEOID'],countyGEOIDs))[0]

# Combine the shapes for your counties
w = shapefile.Writer()
for i in range(len(idxShapes)):
    w._shapes.extend(shps[idxShapes[i]])
outlines = pd.DataFrame(w._shapes,columns=['x','y'])
pathsOut = path.Path(w._shapes)

# Generate coordinates inside the bounding box of the outline
xRng = np.linspace(min(outlines['x']),max(outlines['x']),num=ptResolution)
yRng = np.linspace(min(outlines['y']),max(outlines['y']),num=ptResolution)
x_pts,y_pts = np.meshgrid(xRng,yRng)
x_pts = x_pts.flatten()
y_pts = y_pts.flatten()

# Remove points outside the outline
isInside = pathsOut.contains_points(np.vstack((x_pts,y_pts)).T)
x_pts = x_pts[isInside]
y_pts = y_pts[isInside]

# Plot the outlines and the points inside
plt.plot(outlines['x'],outlines['y'])
plt.scatter(x_pts,y_pts)
plt.show()

#%% Get Distance Matrix from Bing API
# --------------------------------------------------------

try:
    tempLoad = open('tempResults.txt','r')
    result = json.load(tempLoad)
    tempLoad.close()
except IOError:
    # My API key is stored in a seperate file
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
    
    # Request distance matrix from API
    request = urllib.request.Request(theUrl)
    response = urllib.request.urlopen(request)
    
    r = response.read().decode(encoding="utf-8")
    result = json.loads(r)
    
    # Save off the result (so as not to call it again)
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

#%% Align the points via PCA
# --------------------------------------------------------
pcaDist = PCA(n_components=2)
pcaTime = PCA(n_components=2)
distCoords = pcaDist.fit_transform(np.stack((x_pts,y_pts)).T)
timeCoords = pcaTime.fit_transform(np.stack((coords[:,0],coords[:,1])).T)
x_t = coords[:,0]
y_t = coords[:,1]

# rotate time coordinates to align
angle_d = np.arctan2(pcaDist.components_[0,1],pcaDist.components_[0,0])
angle_t = np.arctan2(pcaTime.components_[0,1],pcaTime.components_[0,0])
print(angle_d)
print(angle_t)
angle = -angle_t -np.pi

ox = np.mean(x_t)
oy = np.mean(y_t)
x_time = ox + np.cos(angle)*(x_t - ox) - np.sin(angle)*(y_t - oy)
y_time = oy + np.sin(angle)*(x_t - ox) + np.cos(angle)*(y_t - oy)

# temporary: plot
f, (ax1, ax2) = plt.subplots(1, 2)
ax1.scatter(timeCoords[:,0],timeCoords[:,1])
ax2.scatter(x_time,y_time, marker = 'o')
for i in list(range(len(x_pts))):
    ax1.annotate(str(i),(timeCoords[i,0],timeCoords[i,1]))
    ax2.annotate(str(i),(x_time[i],y_time[i]))
plt.show()

#%% Plotting the results
# --------------------------------------------------------
f, (ax1, ax2) = plt.subplots(1, 2)

ax1.plot(outlines['x'],outlines['y'])
ax1.scatter(x_pts,y_pts)
ax2.scatter(coords[:,0], coords[:,1], marker = 'o')
for i in list(range(len(x_pts))):
    ax1.annotate(str(i),(x_pts[i],y_pts[i]))
    ax2.annotate(str(i),(coords[i,0],coords[i,1]))
plt.show()
