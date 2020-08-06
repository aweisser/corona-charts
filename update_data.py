import requests
url = "https://github.com/owid/covid-19-data/blob/master/public/data/owid-covid-data.json"
data = requests.get(url).json()
print(data)

