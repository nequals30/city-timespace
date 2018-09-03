# stl_distance
Re-projecting the geography of St. Louis by travel time.

Inspired by [Gradient Metrics'](http://gradientmetrics.com/) analysis [*New York City in Timespace*](http://gradientmetrics.com/new-york-city-in-timespace).

This will:
1) Generate a grid of evenly-spaced coordinates that represent the city 
2) Define a polygon that represents the city, remove any points outside of that polygon 
3) Connect to Google Distance API (using googlemaps in Python) to pull down the travel distances between each point and the ones around it 
4) Use Matplotlib to project those in coordinates in Geographic space and in travel-time space.
