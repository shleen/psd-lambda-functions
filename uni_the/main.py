import boto3
import os
import pandas as pd
import shutil
import time
import datetime as dt

from dotenv import load_dotenv
from queue import Queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from tempfile import mkdtemp

from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# basic definitions
year = dt.datetime.now().year
def wait():
    time.sleep(3)
def long_wait():
    time.sleep(5)
def close_cookie(driver):
    try:
        close_btn = driver.find_element(By.XPATH, "//div[@class='eu-cookie-compliance-buttons']")
        close_btn.click()
        wait()
    except:
        print("Cookie button not found")

# THE functions
# Click on "Scores" button
def table_click_scores(driver):
  scores = driver.find_elements(By.XPATH, "//label[contains(@for, 'scores')]")
  scores[0].click()
  wait()


############################################################
############################################################

# chrome driver for THE
def setup_the(year):
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.timeshighereducation.com/world-university-rankings/{year}/subject-ranking/computer-science#!/length/-1/sort_by/rank/sort_order/asc/cols/stats")
    driver.maximize_window()
    long_wait()

    # Check if the page displays the error message
    if "Sorry, we couldn't find that page. Try searching instead." in driver.page_source:
        year -= 1
        driver.quit()
        return setup_the(year)  # Recursively call setup() with the decremented year

    return driver

################################################################################################
################################################################################################
def handler(event=None, context=None):
    # setting up options
    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")    
    prefs = {"download.default_directory": ""}
    options.add_experimental_option("prefs", prefs)

    load_dotenv()

    """""""""""""""""""""""""""""
    THE
    """""""""""""""""""""""""""""
    driver_the = setup_the(year)
    table_click_scores(driver_the)

    time.sleep(20)

    # get uni name
    df_name = driver_the.find_elements(By.XPATH, "//*[contains(@class, 'ranking-institution-title')]")
    name_data = list()
    for i in range(len(df_name)):
        name_data.append(df_name[i].text)

    # get country
    df_country = driver_the.find_elements(By.XPATH, "//div/span")
    country_data = list()
    for i in range(len(df_country)):
        country_data.append(df_country[i].text)

    # get citations
    df_citations = driver_the.find_elements(By.XPATH, "//td[contains(@class, 'scores citations-score')]")
    citations_data = list()
    for i in range(len(df_citations)):
        citations_data.append(df_citations[i].text)

    # get research
    df_research = driver_the.find_elements(By.XPATH, "//td[contains(@class, 'scores research-score')]")
    research_data = list()
    for i in range(len(df_research)):
        research_data.append(df_research[i].text)

    # get teaching
    df_teaching = driver_the.find_elements(By.XPATH, "//td[contains(@class, 'scores teaching-score')]")
    teaching_data = list()
    for i in range(len(df_teaching)):
        teaching_data.append(df_teaching[i].text)

    # Adding data to Dataframe
    df_columns = ["University", "Country", "Citations","Research", "Teaching"]
    df_the = pd.DataFrame(columns=df_columns)

    df_the["University"] = name_data
    df_the["Country"] = country_data
    df_the["Citations"] = citations_data
    df_the["Research"] = research_data
    df_the["Teaching"] = teaching_data

    print(df_the)

    # Upload to S3
    df_the.to_csv("/tmp/the_scrape.csv")
    s3_client = boto3.client('s3')
    timestamp = time.time()
    value = dt.datetime.fromtimestamp(timestamp)
    human_time = value.strftime('%Y-%m-%d ') + str((int(value.strftime('%H'))+8)%24) + value.strftime('%M')
    # TODO: File name changed. Needs to be changed on Workato as well if it breaks.
    s3_client.upload_file("/tmp/the_scrape.csv", "psd-dashboard-data", f"the_scrape {human_time}.csv")
   
# handler()
