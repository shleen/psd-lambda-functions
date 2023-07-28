# Motivation: Find investment data by various sectors/industries/sub-industries and by company to be able to view any emerging trends

# This is the file that should be used to run the actual script. 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup

import time
import pandas as pd

def wait(num=3):
    time.sleep(num)

def long_wait():
    time.sleep(10)

empty_item = "na" #used as the default value for empty cells of data, can also be np.nan

good_items_to_add = "URL, Total Funding, Description, Total Headcount, Country, Sector, Industry, Sub-Industry, Latest Valuation"
items_to_add = good_items_to_add.split(", ")
data_column_names = items_to_add.copy(); data_column_names.insert(0, "Company Name"); data_column_names.insert(0, "Search Input")

sector_columns_str = "Sector, No. Companies, Total Funding (Pre-Exit/IPO)"
sector_columns = sector_columns_str.split(", ")

def remove_criteria(driver):
    all_items_remove = "Connect, URL, Description, Company Status, Company ID, Organization ID, Founded Year, All People, "\
    "Total Headcount, Market Cap, Stock Price, Stock Price (1 week % change), Latest Revenue, Latest Revenue Multiple, "\
    "Mosaic (Overall), Mosaic (Momentum), Mosaic (Money), Mosaic (Market), Mosaic (Management), Competitors, Parent Company, "\
    "Subsidiaries, Sector, Industry, Sub-Industry, Market Reports, Team Tag, Country, Continent, State, City, Street, ZIP Code, "\
    "Total Funding, All Investors, Latest Exit Round, Acquirer, VC Backed, Latest Funding Investors, "\
    "Latest Funding Simplified Round, Latest Funding Amount, Latest Funding Date, Latest Funding Round, Date of Exit, "\
    "Latest Valuation, Your Collections, Expert Collections, Total Headcount, Total Funding, Latest Valuation"
    all_items_to_remove = all_items_remove.split(", "); remove_string_postfix = "-staged-column-remove-button"
    items_not_found = []
    for item in all_items_to_remove:
        try: 
            btn = driver.find_element(By.XPATH, f"//button[@data-test='{item}{remove_string_postfix}']"); btn.click()
        except:
            items_not_found.append(item)
    # print(items_not_found)

def add_criteria(driver):
    for item in items_to_add:
        try:
            btn = driver.find_element(By.XPATH, f"//button[@data-test='{item}-column-button']")
            btn.click()
        except:
            print(f"{btn} not found")

def filter_columns(driver):
    add_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='Add Column']"))
    ) #1
    add_btn.click(); wait()

    remove_criteria(driver); wait() #2
    add_criteria(driver); wait() #3
    
    apply_btn = driver.find_element(By.XPATH, "//button[@data-test='columns-modal-done-button']")
    apply_btn.click()
    wait()

def close_cookie(driver):
    try:
        close_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
            By.XPATH, "//button[@id='pendo-close-guide-75f328f5']"))
        )
        close_btn.click()
        wait()
    except:
        print("Cookie button not found")

def login(driver):
    CB_USERNAME = "YAP_Hui_Keng@imda.gov.sg"; CB_PASSWORD = "1mda12345"
    try:
        email_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter your email address']"))
        )
        email_btn.click(); 
        email_btn.send_keys(CB_USERNAME)
        continue_btn = driver.find_element(By.XPATH, "//span[text()='Continue']")
        continue_btn.click()
        
        password_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter your password']"))
        )
        password_btn.click(); 
        password_btn.send_keys(CB_PASSWORD)
        continue_btn = driver.find_element(By.XPATH, "//span[text()='Log in']")
        continue_btn.click()
        wait(); wait()
    except:
        print("Login not successful")

def setup(headless=False):
    options = webdriver.ChromeOptions()
    # headless means that the browser will not be displayed when running the code
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options) if headless else webdriver.Chrome()
    # driver = webdriver.Chrome()#options=options) time.sleep(10)
    driver.get("https://app.cbinsights.com/i/emerging-tech")
    driver.maximize_window() #; long_wait()

    close_cookie(driver)
    login(driver)

    advanced_search_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='advanced-search-button']"))
    )
    advanced_search_btn.click() #; long_wait()

    filter_columns(driver)

    funding_dropdown_btn = driver.find_element(By.XPATH, "//div[@data-rbd-drag-handle-draggable-id='Total Funding']").find_elements(By.CLASS_NAME, "flexItem--shrink")[1]
    funding_dropdown_btn.click()
    wait()

    desc_btn = driver.find_elements(By.XPATH, "//span[@data-test='High to low']")
    desc_btn[0].click()
    
    return driver

def save_table(df, company, driver, save=False):
    table_element = driver.find_elements(By.CLASS_NAME, "client-reusable-Table-___styles__maxContent___wQTEa")
    table_webpage = table_element[1]
    table_html = table_webpage.get_attribute('outerHTML')
    bs = BeautifulSoup(table_html, "html.parser")

    table = bs.find_all("div", {"class": "client-modules-top-search-components-TableView-___styles__rowWrapper___WLBoH"})

    for row_html in table:
        row = row_html.find_all("div", {"class": "flex-0"})
        row_insert = {}; row_insert['Search Input'] = company

        for index in range(1, len(row)-1):
            item = row[index].text
            text_insert = item if item else empty_item
            row_insert[data_column_names[index]] = text_insert

        df.loc[len(df)] = row_insert
    
    if save:
        df.to_csv('CBI_Firm_Data.csv', index=False)

def save_sector_data(df, industry, driver):
    row_insert = {}
    row_insert[sector_columns[0]] = industry
    
    info = driver.find_element(By.CLASS_NAME, "shadow-sm").find_elements(By.XPATH, "./div")[0]
    funding = info.text.split("Total Funding")[0].split("|")[1]
    num_companies = info.text.split(" ")[0]

    row_insert[sector_columns[1]] = num_companies
    row_insert[sector_columns[2]] = funding

    df.loc[len(df)] = row_insert

def save_all_tables(df, company, driver, iterations=400, save=False):

    save_table(df, company, driver, save=save)
    next_btn = driver.find_element(By.XPATH, "//div[@data-test='Pagebar-Next']").find_element(By.XPATH, "..")
    
    count = 1
    while next_btn.is_enabled():   
        if count >= iterations:
            # used to ensure it doesnt go past 400 pages (2nd failsafe, up to 10 000 members), 1 run had 10 025 for electronics sector
            break 
        if not count % 10:
            print(count, company)
        next_btn.click()
        wait()
        save_table(df, company, driver)
        count += 1

df = pd.DataFrame(columns=data_column_names)
sector_df = pd.DataFrame(columns=sector_columns)

lst_industries = ['Computer Hardware & Services', 
                  'Electronics', 
                  'Media (Traditional)', 
                  'Internet', 
                  'Mobile & Telecommunications', 
                  'Software (non-internet/mobile)']

TIME_START = time.time()

driver = setup()

industries_dropdown_btn = driver.find_element(By.XPATH, "//button[@data-test='filter-section-open-Industries']")
industries_dropdown_btn.click()
wait()

for industry in lst_industries:
    industry_selector_btn = driver.find_element(By.XPATH, "//button[@data-test='tree-filter-popover-trigger-Industries']")
    industry_selector_btn.click()
    wait()

    btn = driver.find_element(By.XPATH, f"//span[text()='{industry}']")
    btn.click()
    wait()
    
    save_sector_data(sector_df, industry, driver)
    save_all_tables(df, industry, driver, iterations=400, save=True)

    clear_industry_btn = driver.find_element(By.XPATH, "//button[@data-test='Industries-on-clear']")
    clear_industry_btn.click()
    wait()


TIME_END = time.time()
TIME_TAKEN = TIME_END - TIME_START
print(f"Execution time: {TIME_TAKEN:.2f} seconds")
print(sector_df)
print(df)

time.sleep(10)
driver.close()
