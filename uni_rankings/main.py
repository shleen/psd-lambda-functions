# import boto3
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

# QS functions
# button to load more data
def click_load_more(driver):
    while True:
        try:
            # Check if the "No data found" message is present
            time.sleep(5)
            no_data_msg = driver.find_element(By.XPATH, "//div[contains(text(), 'No data found on applied filters')]")
            break  # Stop clicking the "Load More" button if the message is found
        except NoSuchElementException:
            pass

        try:
            load_more_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'loadmorebutton') and contains(text(), 'Load More')]")
            driver.execute_script("arguments[0].scrollIntoView();", load_more_btn)
            driver.execute_script("arguments[0].click();", load_more_btn)
            wait()
        except NoSuchElementException:
            # If the "Load More" button is not found, break the loop
            break

# button to scroll right on data table to get other criterias
def table_click_right(driver):
  right_arrow = driver.find_elements(By.XPATH, "//span[@direction='right']")
  right_arrow[0].click()
  wait()

# get locations of schools
def extract_location(driver):
    locations = driver.find_elements(By.XPATH, "//div[contains(@class, 'location')]")
    location_data = []
    for location in locations:
        location_text = location.text.strip()
        if location_text:
            location_data.append(location_text)
    return location_data

# THE functions
# Click on "Scores" button
def table_click_scores(driver):
  scores = driver.find_elements(By.XPATH, "//label[contains(@for, 'scores')]")
  scores[0].click()
  wait()

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
                print("Next Page button is not clickable. Stopping loop.")
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
                print("Next Page button is not clickable. Stopping loop.")
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
                print("Next Page button is not clickable. Stopping loop.")
                break
            next_page_button.click()
            wait()
        except NoSuchElementException as e:
            print("No more pages available.", e)
            break

    return top_numbers



############################################################
############################################################
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

# chrome driver for QS
def setup_qs(year):
    driver = webdriver.Chrome("/opt/chromedriver", options=options) 
    driver.get(f"https://www.topuniversities.com/university-rankings/university-subject-rankings/{year}/computer-science-information-systems?&tab=indicators&sort_by=overallscore&order_by=desc")
    driver.maximize_window()
    long_wait()
    close_cookie(driver)

    # Check if the page contains the "Coming Soon!" error message
    if 'Coming Soon!' in driver.page_source:
        year -= 1
        driver.quit()
        return setup_qs(year)  # Recursively call setup() with the decremented year

    return driver

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

# chrome driver for SH
def setup_sh(year):
    driver = webdriver.Chrome(options=options)
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
    """""""""""""""""""""""""""""
    QS
    """""""""""""""""""""""""""""
    driver_qs = setup_qs(year)
    click_load_more(driver_qs)

    # extract all data
    data = driver_qs.find_elements(By.XPATH, "//*[@class='td-wrap-in']")
    # long_wait()

    # extract indiv data
    # get school names
    schools_data = list()
    for i in range(1, len(data), 8):
        schools_data.append(data[i].text)
    
    # wait()
    table_click_right(driver_qs)

    # get Academic Reputation scores
    AR_data = list()
    for i in range(3, len(data), 8):
        AR_data.append(data[i].text)

    # get Employer Reputation scores
    ER_data = list()
    for i in range(4, len(data), 8):
        ER_data.append(data[i].text)
    
    # get Citations scores
    citations_data = list()
    for i in range(5, len(data), 8):
        citations_data.append(data[i].text)
    
    # get location
    location_data = extract_location(driver_qs)
    country_list = []
    for location in location_data:
        # Check if the location contains a comma
        if ',' in location:
            # Split the string at the comma
            split_location = location.split(',')
            # Remove leading and trailing whitespaces from the city and country
            country = split_location[1].strip()
            country_list.append(country)
        else:        
            country_list.append(None)

    # dataframe
    df_qs = pd.DataFrame()
    df_qs['Country'] = country_list
    df_qs['Country'] = df_qs['Country'].replace("China", "China (Mainland)")
    df_qs["University"] = schools_data
    df_qs["QS Citations per Paper"] = citations_data
    df_qs["QS Employer Reputation"] = ER_data
    df_qs["QS Academic Reputation"] = AR_data
    
    print(df_qs)


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
    


    print("done! :)")

handler()
