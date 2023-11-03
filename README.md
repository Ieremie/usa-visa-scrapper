# usa-visa-scrapper

A selenium script that checks available dates for visa interviews.
It notifies the user by sending a calendar screenshot as an email.

It can also be used to reschedule based on the date preferences automatically.

All you have to do is change the following variables with your own ones.
The MONTH_INDEX is used to go through the calendar. By default, the calendar shows the next two months. If you want to check for later months, increase this index.

You can define the dates you want to reschedule based on the DATE_PREFERENCES. The script selects the first slot (hour) for the first available date.

```python
URL_ID = 1111 # replace with your own URL ID
BASE_URL = f'https://ais.usvisa-info.com/en-gb/niv'
USERNAME = "your visa username"
PASSWORD = "your visa passowrd"
YAHOO_EMAIL = str('your email')
YAHOO_APP_PASSWORD = str('your email app password')

# if True, the script will try to reschedule the appointment
TRY_TO_RESCHEDULE = True
# 0 means the current month and the next month, 1 means the next month and the month after that
MONTH_INDEX = 0
# the dates that you are interested in. The script will try to reschedule to the first available date in this list
DATE_PREFERENCES = {'November': np.arange(3, 16)}
```

![Alt Text](https://github.com/Ieremie/usa-visa-scrapper/blob/main/visa_web_scraper/selenium.gif)
![Alt Text](https://github.com/Ieremie/usa-visa-scrapper/blob/main/visa_web_scraper/output.gif)
