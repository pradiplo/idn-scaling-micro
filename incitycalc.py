from preprocess import preProcess
import numpy as np
from pysal.explore import inequality

class inCityCalc:
    def calc_loubar_threshold(gdf):
        lourank = int(len(gdf)*(1 - gdf["raster_val"].mean()/max(gdf["raster_val"])))
        gdf_rank = gdf.sort_values(by=["raster_val"],ascending=True).reset_index(drop=True)
        return gdf_rank.loc[lourank].raster_val

    def calc_hot_cold(gdf,thres):
        hot = gdf[gdf["raster_val"] >= thres]
        cold = gdf[gdf["raster_val"] < thres]
        gdfhot = hot["raster_val"].sum()
        gdfcold = cold["raster_val"].sum()
        gdf["abc"] = gdf["raster_val"] / max(gdf["raster_val"])
        areahot = gdf["abc"].sum()
        areacold = len(gdf) - gdf["abc"].sum()
        return [gdfhot,gdfcold,areahot,areacold]

    def calc_eta(gdf,thres):
        gdf_dict = gdf["raster_val"].to_dict()
        s = [(k, gdf[k]) for k in sorted(gdf_dict, key=gdf_dict.get)]
        keys = []
        vals = []
        for k,v in s:
            keys.append(k)
            vals.append(v)
        vals = np.array(vals)
        keys = np.array(keys)
        loubar_keys = keys[vals>=threshold]
        dist_mat =  eucl[keys.reshape(-1,1), keys]
        dist_corr = dist_mat[dist_mat>0]
        loubar_dist_mat = eucl[loubar_keys.reshape(-1,1), loubar_keys]
        loubar_dist_corr = loubar_dist_mat[loubar_dist_mat>0]
        eta = loubar_dist_corr.mean()/dist_corr.mean()
        return eta

    def calc_gini(gdf):
        g15 = inequality.gini.Gini(gdf["raster_val"].values)
        gmax = (len(gdf) - 1) / len(gdf)
        gini = g15.g / gmax
        return gini
