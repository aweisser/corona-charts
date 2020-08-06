import urllib.request, json 
with urllib.request.urlopen("https://github.com/owid/covid-19-data/blob/master/public/data/owid-covid-data.json") as url:
    data = json.loads(url.read())
    print(data)
