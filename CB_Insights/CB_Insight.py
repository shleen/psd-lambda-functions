from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import time
import pandas as pd
import pprint

def wait():
    time.sleep(3)
def long_wait():
    time.sleep(5)
def close_cookie(driver):
    try:
        close_btn = driver.find_element(By.XPATH, "//button[@id='pendo-close-guide-75f328f5']")
        close_btn.click()
        wait()
    except:
        print("Cookie button not found")
def login(driver):
    CB_USERNAME = "YAP_Hui_Keng@imda.gov.sg"; CB_PASSWORD = "1mda12345"

    email_btn = driver.find_element(By.XPATH, "//input[@placeholder='Enter your email address']")
    email_btn.click()
    email_btn.send_keys(CB_USERNAME)
    continue_btn = driver.find_element(By.XPATH, "//span[text()='Continue']")
    continue_btn.click()
    wait()

    password_btn = driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
    password_btn.click()
    password_btn.send_keys(CB_PASSWORD)
    continue_btn = driver.find_element(By.XPATH, "//span[text()='Log in']")
    continue_btn.click()
    long_wait()
def setup():
    driver = webdriver.Chrome()
    driver.get("https://app.cbinsights.com/i/emerging-tech")
    driver.maximize_window()
    long_wait()

    close_cookie(driver)
    login(driver)
    
    return driver
def search(company, driver):
    search_field = driver.find_element(By.XPATH, "//input[@id='topSearchInput']")
    search_field.click()
    search_field.send_keys(company)
    wait()

    search_btn = driver.find_element(By.XPATH, "//button[@data-testid='search-button']")
    search_btn.click()
    long_wait()
def remove_criteria(driver):
    all_items_remove = "Connect, URL, Description, Company Status, Company ID, Organization ID, Founded Year, All People, \
    Total Headcount, Market Cap, Stock Price, Stock Price (1 week % change), Latest Revenue, Latest Revenue Multiple, \
    Mosaic (Overall), Mosaic (Momentum), Mosaic (Money), Mosaic (Market), Mosaic (Management), Competitors, Parent Company, \
    Subsidiaries, Sector, Industry, Sub-Industry, Market Reports, Team Tag, Country, Continent, State, City, Street, ZIP Code, \
    Total Funding, All Investors, Latest Exit Round, Acquirer, VC Backed, Latest Funding Investors, \
    Latest Funding Simplified Round, Latest Funding Amount, Latest Funding Date, Latest Funding Round, Date of Exit, \
    Latest Valuation, Your Collections, Expert Collections, Total Headcount, Total Funding, Latest Valuation"
    all_items_to_remove = all_items_remove.split(", "); remove_string_postfix = "-staged-column-remove-button"
    items_not_found = []
    for item in all_items_to_remove:
        try: 
            btn = driver.find_element(By.XPATH, f"//button[@data-test='{item}{remove_string_postfix}']"); btn.click()
        except:
            items_not_found.append(item)
def add_criteria(driver):
    good_items_to_add = "URL, Description, Total Headcount, Country, Sector, Industry, Sub-Industry, Total Funding, Latest Valuation"
    items_to_add = good_items_to_add.split(", ")
    for item in items_to_add:
        try:
            btn = driver.find_element(By.XPATH, f"//button[@data-test='{item}-column-button']")
            btn.click()
        except:
            print(f"{btn} not found")
def filter_columns(driver):
    add_btn = driver.find_element(By.XPATH, "//button[@title='Add Column']")
    add_btn.click(); wait()

    remove_criteria(driver); wait() 
    add_criteria(driver); wait()
    
    apply_btn = driver.find_element(By.XPATH, "//button[@data-test='columns-modal-done-button']")
    apply_btn.click()
def save_search(df, driver):
    table_element = driver.find_elements(By.CLASS_NAME, "client-reusable-Table-___styles__maxContent___wQTEa")
    table = table_element[len(table_element)-1].find_elements(By.XPATH, "./div")

    for row in table:
        container = row.find_element(By.XPATH, "./div")
        columns = container.find_elements(By.XPATH, "./div")
        row_insert = {}
        
        for item_index in range(1, len(columns)-1):
            item = columns[item_index]
            if item.text:
                row_insert[data_column_names[item_index-1]] = item.text
            else:
                row_insert[data_column_names[item_index-1]] = "NA"
        
        df.loc[len(df)] = row_insert
        break
    df.to_csv('CBI_Firm_Data.csv', index=False)    

'''
from home page click on "Advanced Search" -> drop down btn for "Industries" -> select by Industry -> change Country selected
'''

firm_names_file = "CB_Insight_Firms.xlsx"
firm_names = pd.read_excel(firm_names_file, sheet_name="Firms", header=0)["Firm"].tolist()

big_string = "URL, Description, Total Headcount, Country, Sector, Industry, Sub-Industry, Total Funding, Latest Valuation"
items_to_add = big_string.split(", ")
data_column_names = items_to_add.copy(); data_column_names.insert(0, "Company Name")

pp = pprint.PrettyPrinter()
df = pd.DataFrame(columns=data_column_names)

driver = setup()

first_company = firm_names[0]
search(first_company, driver)
filter_columns(driver)
# save_search(df, driver)

# for i in range(1, len(firm_names)):
#     company = firm_names[i]
#     search(company, driver)
#     save_search(df, driver)
#     df.to_csv('CBI_Firm_Data.csv', index=False)    

time.sleep(10)
