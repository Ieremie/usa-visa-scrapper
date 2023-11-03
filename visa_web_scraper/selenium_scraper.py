import smtplib
from datetime import datetime
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np

URL_ID = 1111 # replace with your own URL ID
BASE_URL = f'https://ais.usvisa-info.com/en-gb/niv'
USERNAME = "your visa username"
PASSWORD = "your visa passowrd"

CHECK_INTERVAL = 1.5 * 60
TIME_BETWEEN_CLICKS = 0.5

YAHOO_EMAIL = str('your email')
YAHOO_APP_PASSWORD = str('your email app password')


# if True, the script will try to reschedule the appointment
TRY_TO_RESCHEDULE = True
# 0 means the current month and the next month, 1 means the next month and the month after that
MONTH_INDEX = 0
# the dates that you are interested in. The script will try to reschedule to the first available date in this list
DATE_PREFERENCES = {'November': np.arange(3, 16)}

def send_email_with_screenshot(photo, message="Visa Appointment Change Notification"):
    msg = MIMEMultipart()
    msg['From'] = YAHOO_EMAIL
    msg['To'] = YAHOO_EMAIL
    msg['Subject'] = message

    text = MIMEText(message)
    msg.attach(text)

    image = MIMEImage(photo, name="screenshot.png")
    msg.attach(image)

    server = smtplib.SMTP_SSL("smtp.mail.yahoo.com")
    server.login(YAHOO_EMAIL, YAHOO_APP_PASSWORD)
    server.sendmail(YAHOO_EMAIL, YAHOO_EMAIL, msg.as_string())
    server.quit()


def log_in(driver):
    if driver.current_url != BASE_URL + '/users/sign_in':
        print('Already logged.', driver.current_url)
        return

    print('Logging in.')
    # Clicking the first prompt, if there is one
    try:
        driver.find_element(By.XPATH, '/html/body/div/div[3]/div/button').click()
    except:
        pass
    # Filling the user and password
    driver.find_element(By.NAME, 'user[email]').send_keys(USERNAME)
    driver.find_element(By.NAME, 'user[password]').send_keys(PASSWORD)
    # Clicking the checkbox and Clicking 'Sign in'
    driver.find_element(By.XPATH, '//*[@id="sign_in_form"]/div/label/div').click()
    driver.find_element(By.XPATH, '//*[@id="sign_in_form"]/p/input').click()

    time.sleep(3)
    print('Logged in.')

def get_appointment_page(url, driver):
    # Log in
    while True:
        try:
            driver.get(url)
            print(driver.current_url)
            log_in(driver)
            break
        except ElementNotInteractableException:
            time.sleep(5)

def available_dates(driver):
    """
    By default we look at the current two months that are displayed on the calendar.
    Increasing the month_index will offset the months by one month.
    E.g. month_index=0 looks at the current and next month
            month_index=1 looks at the next and next+1 month
    """

    # click to show the calendar, this opens the calendar for the current month and next month
    try:
        time.sleep(TIME_BETWEEN_CLICKS)
        driver.find_element(By.XPATH, '//*[@id="appointments_consulate_appointment_date"]').click()
        # press the next month button
        for i in range(MONTH_INDEX):
            time.sleep(TIME_BETWEEN_CLICKS)
            driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div[2]/div/a/span').click()

    except ElementNotInteractableException:
        print('Calendar is not even an option.')
        # check if this message appears:
        text = "There are no available appointments at the selected location. Please try again later"
        if text in driver.page_source:
            print(text)
        return False

    return len(driver.find_elements_by_css_selector("a.ui-state-default")) > 0

def reschedule(driver):

    first_month = driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div[1]/div/div/span[1]').text
    second_month = driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div[2]/div/div/span[1]').text

    first_month_dates = driver.find_elements_by_css_selector("div.ui-datepicker-group.ui-datepicker-group-first a.ui-state-default")
    second_month_dates = driver.find_elements_by_css_selector("div.ui-datepicker-group.ui-datepicker-group-last a.ui-state-default")

    available_dates = {}
    available_dates[first_month] = first_month_dates
    available_dates[second_month] = second_month_dates

    # get the first available date from our preferences
    selected_date = None
    for month, dates in available_dates.items():
        if month in DATE_PREFERENCES:
            for date in dates:
                if int(date.text) in DATE_PREFERENCES[month]:
                    print(f"Found a date in {month} that we like: {date.text}")
                    selected_date = date
                    break

    if selected_date is None:
        print("No available date in our preferences")
        return False

    print("Trying to reschedule. Clicking on the first available date")
    selected_date.click()
    time.sleep(TIME_BETWEEN_CLICKS)

    print("Clicking on the drop down menu")
    driver.find_element(By.XPATH, '//*[@id="appointments_consulate_appointment_time"]').click()
    time.sleep(TIME_BETWEEN_CLICKS)

    print("Clicking on the first available time")
    # sometimes the list is empty (probably because it was booked in the meantime)
    try:
        driver.find_element(By.XPATH, '//*[@id="appointments_consulate_appointment_time"]/option[2]').click()
        time.sleep(TIME_BETWEEN_CLICKS)
    except ElementNotInteractableException:
        print("No available time")
        return False

    print("Click on the box to remove drop down menu")
    driver.find_element(By.XPATH, '//*[@id="consulate-appointment-fields"]').click()
    time.sleep(TIME_BETWEEN_CLICKS)

    print("Clicking on the 'Reschedule' button")
    driver.find_element(By.XPATH, '//*[@id="appointments_submit"]').click()
    time.sleep(TIME_BETWEEN_CLICKS)

    print("Clicking on the 'Confirm' button")
    driver.find_element(By.XPATH, '/html/body/div[6]/div/div/a[2]').click()
    time.sleep(TIME_BETWEEN_CLICKS)

    print("Rescheduling was successful")
    return True


def run_visa_scraper(url=f'{BASE_URL}/schedule/{URL_ID}/appointment'):

    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    while True:
        print(f'Starting a new check at {str(datetime.now())}.')
        get_appointment_page(url, driver)

        if available_dates(driver):
            print('A new date was found. Notifying it.')
            send_email_with_screenshot(driver.get_screenshot_as_png())

            if TRY_TO_RESCHEDULE:
                if reschedule(driver):
                    # stop the script
                    send_email_with_screenshot(driver.get_screenshot_as_png(), message="Visa Appointment Rescheduled")
                    driver.close()
                    exit()
                else:
                    print(f'Rescheduling failed. Checking again in {CHECK_INTERVAL} seconds.')
                    time.sleep(CHECK_INTERVAL)

        else:
            print(f'No available dates were found. Checking again in {CHECK_INTERVAL} seconds.')
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run_visa_scraper()
