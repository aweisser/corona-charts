import requests, json
from datetime import datetime
from datetime import timedelta

start_date = "2020-01-01"
dataPoints = []
categories = []

# Get base data
# Group by Refdatum,Altersgruppe as HTML: https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/query?where=&objectIds=&time=&resultType=none&outFields=Refdatum%2CAltersgruppe%2CAnzahlFall%2CAnzahlTodesfall&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=Refdatum+desc&groupByFieldsForStatistics=Refdatum%2CAltersgruppe&outStatistics=%5B%0D%0A++%7B%0D%0A++++%22statisticType%22%3A+%22sum%22%2C%0D%0A++++%22onStatisticField%22%3A+%22AnzahlFall%22%2C%0D%0A++++%22outStatisticFieldName%22%3A+%22AnzahlFall%22%0D%0A++%7D%2C%0D%0A++%7B%0D%0A++++%22statisticType%22%3A+%22sum%22%2C%0D%0A++++%22onStatisticField%22%3A+%22AnzahlTodesfall%22%2C%0D%0A++++%22outStatisticFieldName%22%3A+%22AnzahlTodesfall%22%0D%0A++%7D%0D%0A%5D&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=html&token=
url = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/query?where=&objectIds=&time=&resultType=none&outFields=Refdatum%2CAltersgruppe%2CAnzahlFall%2CAnzahlTodesfall&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=Refdatum+desc&groupByFieldsForStatistics=Refdatum%2CAltersgruppe&outStatistics=%5B%0D%0A++%7B%0D%0A++++%22statisticType%22%3A+%22sum%22%2C%0D%0A++++%22onStatisticField%22%3A+%22AnzahlFall%22%2C%0D%0A++++%22outStatisticFieldName%22%3A+%22AnzahlFall%22%0D%0A++%7D%2C%0D%0A++%7B%0D%0A++++%22statisticType%22%3A+%22sum%22%2C%0D%0A++++%22onStatisticField%22%3A+%22AnzahlTodesfall%22%2C%0D%0A++++%22outStatisticFieldName%22%3A+%22AnzahlTodesfall%22%0D%0A++%7D%0D%0A%5D&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token="
dataPoints = list(requests.get(url).json()["features"])

print(f"Got '{len(dataPoints)}' data points.")

categoryKey = 'Altersgruppe'
dateKey = 'Refdatum'

# Parse different catagories
for dataPoint in dataPoints:
    dataPoint = dataPoint['attributes']
    category = dataPoint[categoryKey]
    
    # Extend list of selectable locations
    categories.append(category)

categories = sorted(set(categories))

for category in categories:
    categoryDataPointsDict = {
        datetime.fromtimestamp(int(d['attributes']['Refdatum']/1000)).strftime("%Y-%m-%d")
        :
        d['attributes'] for d in dataPoints if d['attributes'][categoryKey] == category
    }
    print(f"Got '{len(categoryDataPointsDict)}' data points for category {category}.")

    categoryData = {
        "name": category,
        "data": []
    }

    # create a data entry for every day from start_date to now, even if the data sources doesn't provide values.
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    while current_date <= datetime.now():

        # init data entry for this day
        date = current_date.strftime("%Y-%m-%d")
        day = { "date": date }
        dayData = categoryDataPointsDict.get(date)
        if dayData:
            day = dayData
            day['date'] = date

        # add day to country data
        categoryData["data"].append(day)

        # increment date by one day
        current_date += timedelta(days=1)

    # regenerate .json file for this country
    with open('data/age-groups/'+category+'.json', 'w') as category_data_file:
        json.dump(categoryData, category_data_file, indent=2)

# regenerate categories.json
with open('age-groups.json', 'w') as categories_file:
    json.dump(categories, categories_file, indent=2)
