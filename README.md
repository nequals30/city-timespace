# city-timespace
Re-projecting the geography of a city by travel time.

Inspired by [Gradient Metrics'](http://gradientmetrics.com/) analysis [*New York City in Timespace*](http://gradientmetrics.com/new-york-city-in-timespace).

This will work for any set of US counties, but it can be extended to use other shapes available from the US census.

### How To Use
1) You'll need these libraries if you don't already have them:
	* numpy, pandas, and matplotlib
	* scikit-learn
	* pyshp
	* json

### What it Does
1) Generate evenly-spaced coordinates within the boundaries of the outlines of the US counties you want.
2) Connect to [Bing Maps API](https://msdn.microsoft.com/en-us/library/mt827298.aspx) and pull down travel distances between all the points.
3) Use [Multidimensional Scaling](https://en.wikipedia.org/wiki/Multidimensional_scaling) (aka Principal Coordinate Analysis) to turn the distance matrix into coordinates in time-space.
4) Align the distance-space coordinates and the time-space coordinates using regular PCA
5) Plot the coordinates using Matplotlib

