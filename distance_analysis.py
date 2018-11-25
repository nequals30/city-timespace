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
import matplotlib.tri as tri
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
for i in idxShapes:
    w._shapes.extend(shps[i])
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
plt.axis('equal')
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
pcaD = PCA(n_components=2)
pcaT = PCA(n_components=2)
d_pca = pcaD.fit_transform(np.stack((x_pts,y_pts)).T)
t_pca = pcaT.fit_transform(np.stack((coords[:,0],coords[:,1])).T)

def rotateAroundCentroid(angle,x,y):
    ox = np.mean(x)
    oy = np.mean(y)
    x_rot = ox + np.cos(angle)*(x - ox) - np.sin(angle)*(y - oy)
    y_rot = oy + np.sin(angle)*(x - ox) + np.cos(angle)*(y - oy)
    return x_rot,y_rot

# rotating by -t will put it into pca space, where D and T should be the same
angle_t = np.arctan2(pcaT.components_[:,1],pcaT.components_[:,0])
x_time,y_time = rotateAroundCentroid(-angle_t[0],coords[:,0],coords[:,1])

if angle_t[0]-angle_t[1] == np.pi/2:
    y_time = -y_time
    
# rotating it back by +p should align it with D
angle_d = np.arctan2(pcaD.components_[:,1],pcaD.components_[:,0])
x_time,y_time = rotateAroundCentroid(angle_d[0],x_time,y_time)

# additional nudge
nudge = 30
x_time,y_time = rotateAroundCentroid(np.deg2rad(nudge),x_time,y_time)

#%% Plotting the results
# --------------------------------------------------------
f, (ax1, ax2) = plt.subplots(1, 2)

usedC = np.sqrt((x_pts)**2 + (y_pts)**2)
usedCmap = plt.cm.gist_rainbow
labelSize = 5

# -- Plot Distance Space
ax1.set_title('DISTANCE')
for i in idxShapes:
    thisOutline = np.array(shps[i])
    ax1.plot(thisOutline[:,0],thisOutline[:,1])
ax1.scatter(x_pts,y_pts,c=usedC,cmap=usedCmap)
ax1.set_xlabel('LATITUDE', fontsize=labelSize,fontweight='bold')
ax1.set_ylabel('LONGITUDE', fontsize=labelSize,fontweight='bold')

# -- Plot Time-Space
ax2.set_title('TIME', fontname="Arial", fontsize=12)
ax2.scatter(x_time, y_time,c=usedC,cmap=usedCmap)
ax2.set_xlabel('MINUTES BY CAR', fontsize=labelSize,fontweight='bold')
ax2.set_ylabel('MINUTES BY CAR', fontsize=labelSize,fontweight='bold')

# -- Making Plots Look Better
for ax in (ax1, ax2):
    x0,x1 = ax.get_xlim()
    y0,y1 = ax.get_ylim()
    ax.set_aspect(abs(x1-x0)/abs(y1-y0))
    
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    
    ax.tick_params(labelsize=5)
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

# -- Number the points, for debugging:
#for i in list(range(len(x_pts))):
#    ax1.annotate(str(i),(x_pts[i],y_pts[i]))
#    ax2.annotate(str(i),(x_time[i],y_time[i]))

f.savefig('test.png', dpi=300)
plt.show()
