import requests
from pprint import pprint
import json
import datetime as dt
import calendar


# url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=59.28&lon=17.54"
url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=59.28&lon=17.54"

# weather images at https://github.com/metno/weathericons/tree/main/weather/png
# ex https://github.com/metno/weathericons/blob/main/weather/png/clearsky_day.png

sitename = "www.fixitnow.se, sofia@fixitnow.se"  # for User-Agent

session = requests.Session()

try:
    response = session.get(url, headers={"user-agent": sitename})
except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.RequestException, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
    print("No internet connection")
    exit()

if response.status_code == 200:
    yr = json.loads(response.text)

    # pprint(yr)
    # print(yr['properties']['timeseries'][0]['time'])

    temp_unit = yr['properties']['meta']['units']['air_temperature']

    for time in yr['properties']['timeseries']:

        dt_weather = dt.datetime.fromisoformat(time['time'])

        # if to only show today? compare time date with now date

        # today = dt.datetime.now().date()
        today = dt.datetime.today().date()
        tomorrow = today + dt.timedelta(days=+1)
        # print(dt_weather.date().weekday()) # Return the day of the week as an integer, where Monday is 0 and Sunday is 6.

        # print(f"{dt_weather.strftime('%Y-%m-%d %H:%M')}: {str(time['data']['instant']['details']['air_temperature'])} {temp_unit}")
        if dt_weather.date() == today:
            print(f"Today {dt_weather.strftime('%H:%M')}: {
                  str(time['data']['instant']['details']['air_temperature'])} {temp_unit}")
        elif dt_weather.date() == tomorrow:
            print(f"Tomorrow {dt_weather.strftime('%H:%M')}: {
                  str(time['data']['instant']['details']['air_temperature'])} {temp_unit}")
        else:
            print(f"{calendar.day_name[dt_weather.date().weekday()]} {dt_weather.strftime(
                '%H:%M')}: {str(time['data']['instant']['details']['air_temperature'])} {temp_unit}")


# {'meta': {'units': {'air_pressure_at_sea_level': 'hPa',
#                    'air_temperature': 'celsius',
#                    'cloud_area_fraction': '%',
#                    'precipitation_amount': 'mm',
#                    'relative_humidity': '%',
#                    'wind_from_direction': 'degrees',
#                    'wind_speed': 'm/s'},
#          'updated_at': '2023-11-13T12:41:26Z'},
# 'timeseries': [{'data': {'instant': {'details': {'air_pressure_at_sea_level': 1006.0,
#                                                  'air_temperature': 2.2,
#                                                  'cloud_area_fraction': 100.0,
#                                                  'relative_humidity': 84.6,
#                                                  'wind_from_direction': 326.0,
#                                                  'wind_speed': 5.1}},
#                          'next_12_hours': {'summary': {'symbol_code': 'cloudy'}},
#                          'next_1_hours': {'details': {'precipitation_amount': 0.0},
#                                           'summary': {'symbol_code': 'cloudy'}},
#                          'next_6_hours': {'details': {'precipitation_amount': 0.0},
#                                           'summary': {'symbol_code': 'cloudy'}}},
#                 'time': '2023-11-13T13:00:00Z'},
