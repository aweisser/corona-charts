import requests, json, sys
from datetime import datetime

result = []
locations = []

# Get base data from OurWorldInData source.
url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.json"
owidWorld = requests.get(url).json()
result = list(owidWorld.values())

# Enhance the base data with additional data from JHU
url = "https://pomber.github.io/covid19/timeseries.json"
jhuWorld = requests.get(url).json()
for country in result:
    location = country["location"]
    locations.append(location)

    # Some locations have different names in JHU data set
    if location == "United States":
        jhuCountry = jhuWorld["US"]
    elif location == "Czech Republic":
         jhuCountry = jhuWorld["Czechia"]
    else:
        # avoid KeyError by using get
        jhuCountry = jhuWorld.get(location)
    
    # Some locations does not exist in JHU data set
    if not jhuCountry:
        print(f"Location '{location}' does not exist in JHU data set.")
        continue

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

with open('locations.json', 'w') as outfile:
    json.dump(locations, outfile, indent=2)