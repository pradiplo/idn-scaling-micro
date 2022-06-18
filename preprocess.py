import numpy as np
import pandas as pd
import geopandas as gpd
from rasterio import features
import rasterio.mask
import rioxarray
import xarray
import shapely
from shapely.geometry import shape as shaping
import utils


class preProcess:

    def obtainCityDf(countryName):
        ghs_all = gpd.read_file("./raws/GHS_FUA_UCDB2015_GLOBE_R2019A_54009_1K_V1_0.gpkg")
        ghs_all = ghs_all.to_crs("epsg:4326")
        ghs_all = ghs_all[~ghs_all.eFUA_name.str.contains('nan',na=False)]
        ghs_all = ghs_all[~ghs_all.eFUA_name.str.contains('N/A',na=False)]
        ghs_all = ghs_all[~ghs_all.eFUA_name.str.contains('Unit 1',na=False)]
        ghs_all = ghs_all[~ghs_all.eFUA_name.str.contains('Kogimage',na=False)]
        ghs_indo = ghs_all[ghs_all.Cntry_name.str.contains(countryName)].reset_index(drop=True)
        ghs_indo = ghs_indo.sort_values(by=["FUA_p_2015"]).reset_index(drop=True)
        ghs_indo = ghs_indo.set_index("eFUA_ID", drop=False)
        ghs_indo["Comm_area"] = ghs_indo["FUA_area"] - ghs_indo["UC_area"]
        popDict = ghs_indo["FUA_p_2015"].to_dict()
        areaDict = ghs_indo["FUA_area"].to_dict()
        aUCDict = ghs_indo["UC_area"].to_dict()
        aComDict = ghs_indo["Comm_area"].to_dict()
        return [ghs_indo, popDict, areaDict, aUCDict, aComDict]

    def mask_read(rasfile, shape_geoser,i):
        with rasterio.open(rasfile) as src:
            crs=src.crs
            shape_geoser=shape_geoser.to_crs(crs)
            shape=shape_geoser.values
            out_image, out_transform = rasterio.mask.mask(src, shape, crop=True)
            out_meta = src.meta
            out_meta.update({"driver":"GTiff",
                             "height":out_image.shape[1],
                             "width":out_image.shape[2],
                             "transform": out_transform})
        with rasterio.open("./temps/masked_"+str(i)+".tif", "w", **out_meta) as dest:
            dest.write(out_image)
        dlocs="./temps/masked_"+str(i)+".tif"

        ##############workaround of rasterio inability in polygonizing each pixel############
        with rasterio.open(dlocs) as f:
            data_res=f.read(1, out_dtype=np.float32) # make a fake data (final storage array that has real data's shape with float dtype)
            data=f.read(1, out_dtype=np.int32) #real data

            #enum of 2d array to be put after . digit as index-like number of each value
            #eg: array[1,1] value 10 ==> value=10.11| done this to make all value unique
            #for d1i, d1d in enumerate (data):
            #    for d2i, d2d in enumerate(d1d):
            #        if d2d >0:
            #            num=str(d2d)+"."+str(d1i)+str(d2i) #put  index-like number after .
            #            data_res[d1i,d2i]=float(num)
            shapes = rasterio.features.shapes(data,transform=f.transform)

        values= []
        geometry = []
        for shapedict, value in shapes:
            values.append(value)
            geometry.append(shaping(shapedict))

        gdf = gpd.GeoDataFrame( {'raster_val': values, 'geometry': geometry },crs=crs)
        gdf=gdf[gdf["raster_val"]>0]

        return gdf.reset_index(drop=True)

    def obtainGDP(countryName):
        citydf = preProcess.obtainCityDf(countryName)[0]
        cityIndex = citydf["eFUA_ID"].tolist()
        gdpDict = {k: [] for k in cityIndex}
        totGdpDict = {k: [] for k in cityIndex}
        xds = xarray.open_dataset('./raws/GDP_PPP_30arcsec_v3.nc')
        xds.rio.write_crs("epsg:4326", inplace=True)
        at=[x for x in xds]

        for x in xds[at[-1]]:
            if x["time"] == 2015:
                x.rio.to_raster('./temps/gdp_temp.tif')

        for place in cityIndex:
            boundaries = gpd.GeoSeries(citydf.loc[place].geometry)
            boundaries.crs = "epsg:4326"
            gdp_gdf = preProcess.mask_read("./temps/gdp_temp.tif",boundaries,"gdp")
            totgdp = gdp_gdf["raster_val"].sum()
            gdpDict[place] = gdp_gdf
            totGdpDict[place] = totgdp

        return [gdpDict,totGdpDict]

    def obtainCountryBoundary(country, level):
        #country ="./raws/gadm36_IDN_shp/gadm36_IDN_1.shp"
        #negara = gpd.read_file(country)
        negara=utils.get_adm_country(country, level)
        negara["titik_time"]=negara.centroid
        negara["titik_time"]=negara["titik_time"].apply(lambda x: utils.time_zoning(x))
        negara["titik_time"] = negara["titik_time"].astype(str).str.replace("Asia/Pontianak","Asia/Jakarta")
        negara=negara.to_crs("EPSG:4326")
        return negara
