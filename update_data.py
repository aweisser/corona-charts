import requests, json, sys
from datetime import datetime

#outfile_name = sys.argv[1]
countries = ["DEU", "FRA", "ITA", "USA", "IND", "GBR", "SWE"]
result = []

# Get base data from OurWorldInData source.
url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.json"
owidWorld = requests.get(url).json()
for country in countries:
    result.append(owidWorld[country])

# Enhance the base data with additional data from JHU
url = "https://pomber.github.io/covid19/timeseries.json"
jhuWorld = requests.get(url).json()
for country in result:
    location = country["location"]
    # Some locations have different names in JHU data set
    if location == "United States":
        location = "US"
    jhuCountry = jhuWorld[location]
    jhuCountryDict = { datetime.strptime(day["date"], "%Y-%m-%d").strftime("%Y-%m-%d") : day for day in jhuCountry }
    total_recovered = 0
    for day in country["data"]:
        try:
            jhuDay = jhuCountryDict[day["date"]]
            day["total_recovered"] = jhuDay["recovered"]
            day["new_recovered"] = jhuDay["recovered"] - total_recovered
            total_recovered = jhuDay["recovered"]
        except:
            print(location, day["date"], "not found in JHU data set")
    
    # regenerate outfile
    with open('data/'+location+'.json', 'w') as outfile:
        json.dump(country, outfile, indent=2)