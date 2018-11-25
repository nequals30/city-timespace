# city-timespace
Re-projecting the geography of a city by travel time.

Inspired by [Gradient Metrics'](http://gradientmetrics.com/) analysis [*New York City in Timespace*](http://gradientmetrics.com/new-york-city-in-timespace).

This works for any set of US counties, but it can be extended to use other shapes available from the US census.
## Examples

## How To Use
1) You'll need these libraries if you don't already have them:
	* numpy, pandas, and matplotlib
	* scikit-learn
	* pyshp
	* json
2) Download the shapefiles from census.gov (I used the 500k ones). Unzip the contents into the same directory as this script. County shapefiles are [HERE](https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html),  but the analysis would work with any shapefiles, such as urban area, zip code, or even state or nation. Those can be found [HERE](https://www.census.gov/geo/maps-data/data/tiger-cart-boundary.html).
3) Get a Bing Maps API key by following [these instructions](https://msdn.microsoft.com/en-us/library/ff428642.aspx). 
4) Look up the GEOID of areas you want to show from [HERE](https://census.missouri.edu/geocodes/). Enter them in as strings in the "settings" section of the code:
```python
countyGEOIDs = ['29510','29189'] #st. louis city and county
```

## How it Works
1) Generate evenly-spaced coordinates within the boundaries of the outlines of the US counties you want.
2) Connect to [Bing Maps API](https://msdn.microsoft.com/en-us/library/mt827298.aspx) and pull down travel distances between all the points.
3) Use [Multidimensional Scaling](https://en.wikipedia.org/wiki/Multidimensional_scaling) (aka Principal Coordinate Analysis) to turn the distance matrix into coordinates in time-space.
4) Align the distance-space coordinates and the time-space coordinates using regular PCA
5) Plot the coordinates using Matplotlib

