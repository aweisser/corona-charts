import requests, json, re
from datetime import datetime
from datetime import timedelta

start_date = "2020-03-01"
dataPoints = []
categories = []
categoryKey = 'Altersgruppe'
dateKey = 'Refdatum'
categoryPattern = re.compile(r'^(A\d\d)(-|\+)(A\d\d)?$')

# Get base data
# Group by Refdatum,Altersgruppe as HTML: https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/query?where=&objectIds=&time=&resultType=none&outFields=Refdatum%2CAltersgruppe%2CAnzahlFall%2CAnzahlTodesfall&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=Refdatum+desc&groupByFieldsForStatistics=Refdatum%2CAltersgruppe&outStatistics=%5B%0D%0A++%7B%0D%0A++++%22statisticType%22%3A+%22sum%22%2C%0D%0A++++%22onStatisticField%22%3A+%22AnzahlFall%22%2C%0D%0A++++%22outStatisticFieldName%22%3A+%22AnzahlFall%22%0D%0A++%7D%2C%0D%0A++%7B%0D%0A++++%22statisticType%22%3A+%22sum%22%2C%0D%0A++++%22onStatisticField%22%3A+%22AnzahlTodesfall%22%2C%0D%0A++++%22outStatisticFieldName%22%3A+%22AnzahlTodesfall%22%0D%0A++%7D%0D%0A%5D&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=html&token=
url = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/query?where=&objectIds=&time=&resultType=none&outFields=Refdatum%2CAltersgruppe%2CAnzahlFall%2CAnzahlTodesfall&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=Refdatum+desc&groupByFieldsForStatistics=Refdatum%2CAltersgruppe&outStatistics=%5B%0D%0A++%7B%0D%0A++++%22statisticType%22%3A+%22sum%22%2C%0D%0A++++%22onStatisticField%22%3A+%22AnzahlFall%22%2C%0D%0A++++%22outStatisticFieldName%22%3A+%22AnzahlFall%22%0D%0A++%7D%2C%0D%0A++%7B%0D%0A++++%22statisticType%22%3A+%22sum%22%2C%0D%0A++++%22onStatisticField%22%3A+%22AnzahlTodesfall%22%2C%0D%0A++++%22outStatisticFieldName%22%3A+%22AnzahlTodesfall%22%0D%0A++%7D%0D%0A%5D&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token="
dataPoints = list(requests.get(url).json()["features"])
print(f"Got '{len(dataPoints)}' data points from arcgis.")

# Get additional population by age data from Genesis (Statistisches Bundesamt)
# Human readable version of this data table: https://www-genesis.destatis.de/genesis//online?operation=table&code=12411-0005&bypass=true&levelindex=0&levelid=1640791908447#abreadcrumb
urlGenesis = "https://www-genesis.destatis.de/genesisWS/rest/2020/data/tablefile?username=DE8CNGS5G6&password=UrMjX%s4Tcwm78ADUdv%&language=de&name=12411-0005&timeslices=1&format=ffcsv"
populationCsv = requests.get(urlGenesis).content
# Ignore the first row (header) and grep the last column of each row. This is the population. The index of the resulting array is the age.
populationList = [ int(row.split(b';').pop()) for row in populationCsv.splitlines()[1:] ]
# The last row is the total population. Get the last row and remove it from the list.
populationTotal = populationList.pop()
print(f"Got '{len(populationList)+1}' data points from Genesis.")

# Get additional data about hospitalisation
urlRkiHosp = "https://raw.githubusercontent.com/robert-koch-institut/COVID-19-Hospitalisierungen_in_Deutschland/master/Aktuell_Deutschland_COVID-19-Hospitalisierungen.csv"
hospCsv = requests.get(urlRkiHosp).content
# Split by rows and columns and filter only data from whole Germany
hospList = list(filter(lambda row: b'Bundesgebiet' in row ,[row.split(b',') for row in hospCsv.splitlines()]))
hospDict = { (row[0]+b" "+row[3]).decode("utf-8") : int(row[4]) for row in hospList }
print(f"Got {len(hospDict)} data points from RKI Github.")

# Parse different catagories
for dataPoint in dataPoints:
    dataPoint = dataPoint['attributes']
    category = dataPoint[categoryKey]
    # Extend list of selectable locations only if the category matches the pattern
    if categoryPattern.match(category):
        categories.append(category)

categories = sorted(set(categories))

for category in categories:

    categoryDataPointsDict = {
        datetime.fromtimestamp(int(d['attributes']['Refdatum']/1000)).strftime("%Y-%m-%d")
        :
        d['attributes'] for d in dataPoints if d['attributes'][categoryKey] == category
    }
    print(f"Got '{len(categoryDataPointsDict)}' data points for category {category}.")

    # sum up population for this age group
    range = [ int(n) for n in category.replace('A', '').replace('+', '').split('-') ]
    if len(range) == 1:
        population = sum(populationList[range[0]:])
    if len(range) == 2:
        population = sum(populationList[range[0]:range[1]+1])

    categoryData = {
        "name": category,
        "populationTotal": populationTotal,
        "population": population,
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

        # Add hospitalisation for this day and category
        hospValue = hospDict.get(date+' '+category.replace('A', ''))
        if hospValue:
            day['AnzahlHospitalisierung7T'] = hospValue

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
