#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 13:05:37 2018

@author: nequals30 (http://www.nequals30.com)
"""

import googlemaps

# Get API key from config file 
credentials = open('googlemaps_credentials.config','r')
apiKey = credentials.readlines()[0].strip()
credentials.close()

# Connect to Google Maps API
gm = googlemaps.Client(key=apiKey)

print("yo")