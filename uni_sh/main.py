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


# SH functions
# Click CNCI
def click_cnci(driver):
    try:
        button = driver.find_element(By.XPATH, '//*[@id="content-box"]//th[5]//img')
        button.click()
        long_wait()
        cnci = driver.find_element(By.XPATH, '//li[text()="CNCI"]')
        cnci.click()
        wait()
    except Exception as e:
        print("cnci button not found", e)

# Click button to go back to top
def click_top(driver):
    try:
        button = driver.find_element(By.XPATH, '//*[@id="content-box"]//th[5]//img')
        button.click()
        long_wait()
        top = driver.find_element(By.XPATH, '//li[text()="TOP"]')
        top.click()
        wait()
    except Exception as e:
        print("top button not found", e)

# Get names
def extract_names(driver):
    university_names = []
    while True:
        rows = driver.find_elements(By.XPATH, '//tr[@data-v-ae1ab4a8=""]')
        for row in rows:
            university_name_elements = row.find_elements(By.XPATH, './/span[@class="univ-name"]')
            for element in university_name_elements:
                university_name = element.text.strip()
                university_names.append(university_name)  # Append the university name to the list

        try:
            next_page_button = driver.find_element(By.XPATH, '//li[@title="下一页"]')
            if next_page_button.get_attribute('aria-disabled') == 'true':
                # print("Next Page button is not clickable. Stopping loop.")
                break
            next_page_button.click()
            wait()
        except NoSuchElementException as e:
            print("No more pages available.", e)
            break
    
    return university_names

# Get CNCI scores
def extract_cnci(driver):
    cnci_numbers = []
    while True:
        rows = driver.find_elements(By.XPATH, '//tr[@data-v-ae1ab4a8=""]')
        for row in rows:
            td_elements = row.find_elements(By.XPATH, './/td')
            if len(td_elements) >= 5:
                cnci_element = td_elements[4]  # Select the fifth td element (which is the cnci number)
                cnci_number = cnci_element.text.strip()
                cnci_numbers.append(cnci_number)  # Append the CNCI number to the list

        try:
            next_page_button = driver.find_element(By.XPATH, '//li[@title="下一页"]')
            if next_page_button.get_attribute('aria-disabled') == 'true':
                # print("Next Page button is not clickable. Stopping loop.")
                break
            next_page_button.click()
            wait()
        except NoSuchElementException as e:
            print("No more pages available.", e)
            break

    return cnci_numbers

# Get TOP scores
def extract_top(driver):
    top_numbers = []
    while True:
        rows = driver.find_elements(By.XPATH, '//tr[@data-v-ae1ab4a8=""]')
        for row in rows:
            td_elements = row.find_elements(By.XPATH, './/td')
            if len(td_elements) >= 5:
                top_element = td_elements[4]  # Select the fifth td element
                top_number = top_element.text.strip()
                top_numbers.append(top_number)  # Append the top number to the list

        try:
            next_page_button = driver.find_element(By.XPATH, '//li[@title="下一页"]')
            if next_page_button.get_attribute('aria-disabled') == 'true':
                # print("Next Page button is not clickable. Stopping loop.")
                break
            next_page_button.click()
            wait()
        except NoSuchElementException as e:
            print("No more pages available.", e)
            break

    return top_numbers



############################################################
############################################################

# chrome driver for SH
def setup_sh(year):
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

    driver = webdriver.Chrome("/opt/chromedriver", options=options)
    driver.get(f"https://www.shanghairanking.com/rankings/gras/{year}/RS0210")
    driver.maximize_window()
    long_wait()
    
    # Check if the page is inaccessible
    if "Sorry, the page is inaccessible" in driver.page_source:
        year -= 1
        driver.quit()
        return setup_sh(year)  # Recursively call setup() with the decremented year
    
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
    SH
    """""""""""""""""""""""""""""
    driver_sh = setup_sh(year)
    back_to_first_page = driver_sh.find_element(By.XPATH, '//li[@title="1"]')

    # Extract names
    back_to_first_page.click()
    university = extract_names(driver_sh)

    # Extract CNCI
    back_to_first_page.click()
    time.sleep(12)
    driver_sh.execute_script("window.scrollTo(0, 0);")
    time.sleep(3)
    click_cnci(driver_sh)
    time.sleep(10)
    cnci = extract_cnci(driver_sh)

    # Extract TOP
    back_to_first_page.click()
    time.sleep(12)
    driver_sh.execute_script("window.scrollTo(0, 0);")
    time.sleep(3)
    click_top(driver_sh)
    time.sleep(10)
    top = extract_top(driver_sh)

    # Adding data to Dataframe
    df_sh = pd.DataFrame()
    df_sh["University"] = university
    df_sh["CNCI"] = cnci
    df_sh["TOP"] = top

    print(df_sh)

    # Upload to S3
    df_sh.to_csv("/tmp/sh_scrape.csv")
    s3_client = boto3.client('s3')
    timestamp = time.time()
    value = dt.datetime.fromtimestamp(timestamp)
    human_time = value.strftime('%Y-%m-%d ') + str((int(value.strftime('%H'))+8)%24) + value.strftime('%M')
    # TODO: File name changed. Needs to be changed on Workato as well if it breaks.
    s3_client.upload_file("/tmp/sh_scrape.csv", "psd-dashboard-data", f"SH Scrape {human_time}.csv")

# handler()
