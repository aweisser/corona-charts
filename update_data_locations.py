import requests, json, sys
from datetime import datetime
from datetime import timedelta

start_date = "2020-03-01"
owidWorld = []
locations = []

# Get base data from OurWorldInData source.
url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.json"
owidWorld = list(requests.get(url).json().values())

# Get additional data from JHU
url = "https://pomber.github.io/covid19/timeseries.json"
jhuWorld = requests.get(url).json()

# Iterate locations from OWID and enhance with additional data from JHU
for owidCountry in owidWorld:
    location = owidCountry["location"]
    
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

    # Extend list of selectable locations
    locations.append(location)

    # Create dicts with date as keys and day data as values
    owidCountryDict = { datetime.strptime(day["date"], "%Y-%m-%d").strftime("%Y-%m-%d") : day for day in owidCountry["data"] }
    jhuCountryDict = { datetime.strptime(day["date"], "%Y-%m-%d").strftime("%Y-%m-%d") : day for day in jhuCountry }
    
    # init variables for resulting data set
    total_recovered = 0
    country = owidCountry
    country["data"] = []

    # create a data entry for every day from start_date to now, even if the data sources doesn't provide values.
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    while current_date <= datetime.now():

        # init data entry for this day
        date = current_date.strftime("%Y-%m-%d")
        day = { "date": date }
        
        # try to get base data from OWID
        owidDay = owidCountryDict.get(date)
        if owidDay:
            day = owidDay    

        # try to get additional data from JHU
        jhuDay = jhuCountryDict.get(date)
        if jhuDay:
            day["total_recovered"] = jhuDay["recovered"]
            day["new_recovered"] = jhuDay["recovered"] - total_recovered
            total_recovered = jhuDay["recovered"]
        
        # add day to country data
        country["data"].append(day)

        # increment date by one day
        current_date += timedelta(days=1)

    # regenerate .json file for this country
    with open('data/locations/'+location+'.json', 'w') as country_file:
        json.dump(country, country_file, indent=2)

# regenerate locations.json
with open('locations.json', 'w') as locations_file:
    json.dump(locations, locations_file, indent=2)
