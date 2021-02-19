# from django.db import models
import pandas as pd
from .apps import PredictorConfig, PredictorConfigExits
import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import re
from datetime import datetime, timedelta
import numpy as np
import holidays 

number_of_views = 0
data_ws = None


def web_scrape_values():
    soup = BeautifulSoup(urlopen(
        "https://www.theweatheroutlook.com/twoforecasts/hourly-weather-forecast.aspx?lat=51.6&lon=-3.0&loc=Newport,Newport").read(),
                         'html.parser')

    results = soup.find_all('div', attrs={'class': 'overflow-horiz-wrapper'})

    table_data = results[0]

    row_data = table_data.find_all('tr')

    # datetime object containing current date and time
    now = datetime.now()

    data = []

    hours_passed = 0
    start_hour = 0

    for i in row_data:
        hour = i.find_all('td', attrs={'class': 'graycomb-strong'})
        rain = i.find_all('td', attrs={'class': 'raint'})
        temps = i.find_all('td', attrs={'class': 'temps'})
        try:

            hour = int(re.split(":", hour[0].get_text())[0])
            if hours_passed == 0:
                start_hour = hour
            rain = float(re.findall(r'\d+\.?\d*', rain[0].get_text())[0])
            temps = float(re.findall(r'\d+\.?\d*', temps[0].get_text())[0])

            data.append([temps, rain, hour,
                         datetime(now.year, now.month, now.day, start_hour, 0, 0) + timedelta(hours=hours_passed)])
            hours_passed += 1

        except:
            continue

    return data


# Create your models here.

def generate_array(day_of_week):
    day = day_of_week

    day_of_week = []

    x = 0

    while x < 7:
        x += 1
        day_of_week.extend([0])

    day = int(day) - 1
    day_of_week[day] = 1

    return day_of_week


def generate_dataframes(data):
    """TDOO"""
    # print(data)
    prediction = pd.DataFrame(data, columns=["hour_temp", "precipitation", "hour", "Date"])
    prediction["dayofweek"] = prediction.Date.dt.dayofweek
    prediction['Date'] = prediction['Date'].astype(str)
    prediction = prediction.set_index("Date")






    return prediction, prediction.index


def retrieve_bank_holiday(prediction):


    uk_holidays = holidays.UnitedKingdom() 

    holiday_years = []
    prediction.index = pd.to_datetime(prediction.index)

    for date_time in prediction.index.to_pydatetime(): ## Get the values we are predicting
        if len(holiday_years)<1: #If empty add first time
            holiday_years.append(date_time.year)
        for value in holiday_years: #Check if a date hasn't already been added
            if date_time.year == value:
                break #if it has break out of loop
            else:
                holiday_years.append(date_time.year) #else add that day

    holiday_days = []
                
    for year in holiday_years: #retreieve the bank holidays for the speciefied days
        for holiday_day in holidays.UnitedKingdom(years = year).items():
            holiday_days.append(holiday_day[0])
            
    holiday_list = []

    for day in prediction.index.to_pydatetime():
        if day.date() in holiday_days:
            holiday_list.append(1)
        else:
            holiday_list.append(0)
            
    prediction["bank_holiday"] = holiday_list

    return prediction


def tree_model_predict():
    """TDOO"""
    global number_of_views
    global data_ws

    if number_of_views <= 2:
        data_ws = web_scrape_values()

    prediction, index = generate_dataframes(data_ws)
    prediction = retrieve_bank_holiday(prediction)






    values = PredictorConfig.regressor.predict(prediction).astype(int)
    exits = PredictorConfigExits.regressor.predict(prediction).astype(int)

    number_of_views += 1

    name = 'Decision Tree Prediction'
    data = {'Enter': values,
            'Exit': exits
            }

    test = pd.DataFrame(data, index=index)

    return name, test

