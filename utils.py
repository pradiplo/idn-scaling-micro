#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 20:36:36 2022

@author: kunogenta
"""
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import geopandas as gpd
import fiona
import datetime
import pytz
from timezonefinder import TimezoneFinder
#country="IDN"
def get_adm_country(country, level_layer_name):
    #country == county code in gdam
    # level_layer_name = layer name of administrativ level of your choice (write as written in gdam site)
    gdam_base="https://geodata.ucdavis.edu/gadm/gadm4.0/gpkg/"
    soup=bs(requests.get(gdam_base).content,features="lxml")
    text=soup.text.split("\n")
    text=[t for t in text if len(t)>0]
    text=text[4:len(text)-1]
    counties_code=pd.Series(text).str.split(".", expand=True)[0].str.split("_", expand=True)[1].to_list()
    if country not in counties_code:
        print("no such names choose from here: \n",  counties_code)
    else:
        hrefs={}
        for a in soup.find_all("a"):
            href=a.attrs.get("href")
            if ".gpkg" in href:
                key=href.split(".")[0].split("_")[1]
                value=gdam_base+href
                hrefs[key]=value
    
        path=hrefs[country]
        levels=[layername for layername in fiona.listlayers(path)]
        if level_layer_name not in levels:
            print("no such names choose from here: \n", levels)
        else:
            print(f"getting {level_layer_name} file....")
            return gpd.read_file(path, layer=level_layer_name)
tf = TimezoneFinder(in_memory=True)
def time_zoning(g):
    lon,lat=g.xy
    x=lon[0]
    y=lat[0]
    return pytz.timezone(tf.timezone_at(lng=x, lat=y))