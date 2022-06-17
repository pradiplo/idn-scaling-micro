from preprocess import preProcess
from incitycalc import inCityCalc

class country:
    def calc_incity_quantity_all(gdp_raster_dic):
        #gdp_raster_dic = preProcess.obtainGDP(countryName)[0]
        gini = eta = loubar = gdphot = gdpcold = areahot = areacold = {k: [] for k in gdp_raster_dic}
        for place, gdp in gdp_raster_dic.items():
            threshold = inCityCalc.calc_loubar_threshold(gdp)
            loubar[place] = threshold
            hotcold = inCityCalc.calc_hot_cold(gdp,threshold)
            gdphot[place] = hotcold[0]
            gdpcold[place] = hotcold[1]
            areahot[place] = hotcold[2]
            areacold[place] = hotcold[3]
            eta[place] = inCityCalc.calc_eta(gdp,threshold)
            gini[place] = inCityCalc.calc_gini(gdp)
        return [loubar, gdphot, gdpcold, areahot, areacold, eta, gini]


    def plotEtaGiniCluster(etadic, ginidic, popdic):
        #etadic sama ginidic ambil dari fungsi atas
