# city-timespace
Re-projecting the geography of a city by travel time.

Inspired by [Gradient Metrics'](http://gradientmetrics.com/) analysis [*New York City in Timespace*](http://gradientmetrics.com/new-york-city-in-timespace).

This will work for any set of US counties, but it can be extended to use other shapes available from the US census.

### How To Use

### What it Does
1) Generate a grid of evenly-spaced coordinates that represent the city 
2) Define a polygon that represents the city, remove any points outside of that polygon 
3) Connect to [Bing Maps API](https://msdn.microsoft.com/en-us/library/mt827298.aspx) and pull down travel distances between all the points.
4) Use [Multidimensional Scaling](https://en.wikipedia.org/wiki/Multidimensional_scaling) (aka Principal Coordinate Analysis) to turn the distance matrix into coordinates in time-space.
5) Align the distance-space coordinates and the time-space coordinates using regular PCA
6) Plot the coordinates using Matplotlib

