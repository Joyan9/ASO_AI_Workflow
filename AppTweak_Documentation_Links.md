## Current App metadata
Returns metadata from an app that AppTweak has been able to gather from the App Store or the Google Play Store. The data is fetched daily: https://developers.apptweak.com/reference/app-metadata-current.md

```
import requests

url = "https://public-api.apptweak.com/api/public/store/apps/metadata.json?apps=6448311069&country=us&language=us&device=iphone"

headers = {
    "accept": "application/json",
    "x-apptweak-key": API_KEY
}
response = requests.get(url, headers=headers)
print(response.text)
```


## App Historical Metadata
Returns metadata changes from an app that AppTweak has been able to gather from the App Store or the Google Play Store. The data is fetched daily: https://developers.apptweak.com/reference/app-metadata-history.md

Example
```
import requests

url = "https://public-api.apptweak.com/api/public/store/apps/metadata/changes.json?apps=com.tinder&country=us&language=us&device=android&start_date=2022-12-01&end_date=2022-12-14"

headers = {
    "accept": "application/json",
    "x-apptweak-key": API_KEY
}
response = requests.get(url, headers=headers)
print(response.text)
```

## Current Keyword Metrics
Get the most recent metrics of a keyword (volume, difficulty, brand, total results, max reach): https://developers.apptweak.com/reference/keyword-metrics-current.md

```
import requests

url = "https://public-api.apptweak.com/api/public/store/keywords/metrics/current.json?keywords=music%2Cpodcasts%2Csongs&metrics=volume%2Cdifficulty%2Call_installs&country=us&language=us&device=iphone"

headers = {
    "accept": "application/json",
    "x-apptweak-key": "APPTWEAK-API-KEY"
}

response = requests.get(url, headers=headers)

print(response.text)
```

## Historical Keyword Metrics
Get historical metrics of a keyword (volume) for a given date range: https://developers.apptweak.com/reference/keyword-metrics-history.md

```
import requests

url = "https://public-api.apptweak.com/api/public/store/keywords/metrics/history.json?keywords=fitness&metrics=volume&country=us&language=us&device=iphone&start_date=2021-12-24&end_date=2022-01-07"

headers = {
    "accept": "application/json",
    "x-apptweak-key": "APPTWEAK-API-KEY"
}

response = requests.get(url, headers=headers)

print(response.text)
```