import requests, json, sys
outfile_name = sys.argv[1]
url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.json"
source = requests.get(url).json()
countries = ["DEU", "FRA", "ITA", "USA", "IND", "GBR", "SWE"];
result = []
for country in countries:
    result.append(source[country])

with open(outfile_name, 'w') as outfile:
    json.dump(result, outfile)