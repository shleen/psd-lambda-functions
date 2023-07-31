# This will be where to import and execute the final complete script
# This script extracts 16 datasets from United States Bureau of Labor Statistics
# Link: https://data.bls.gov/oes/#/home

"""
This folder contains the Selenium script used to scrape the US BLS website. About the US BLS Website:
The Bureau of Labor Statistics is a unit of the United States Department of Labor. It is the principal fact-finding agency for the U.S. government in the broad field of labor economics and statistics and serves as a principal agency of the U.S. Federal Statistical System
In particular, the Occupational Employment and Wage Statistics section of the US BLS data contains the following data:
1.	Employment
2.	Employment Percent Relative Standard Error
3.	Hourly Mean Wage
4.	Annual Mean Wage
5.	Wage Percent Relative Standard Error
6.	Hourly 10th Percentile Wage
7.	Hourly 25th Percentile Wage
8.	Hourly Median Wage
9.	Hourly 75th Percentile Wage
10.	Hourly 90th Percentile Wage
11.	Annual 10th Percentile Wage
12.	Annual 25th Percentile Wage
13.	Annual Median Wage
14.	Annual 75th Percentile Wage
15.	Annual 90th Percentile Wage
16.	Sectoral Breakdown of Employment by Occupation
For our Policy Questions, we are interested to extract the aforementioned data for tech occupations in the US across all industries. These questions could incorporate the following:
1.	Demand/Vacancies for Tech Occupations with respect to US
2.	Which sectors have the highest employment of tech occupations
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Firefox()
driver.get("https://data.bls.gov/oes/#/home")
print(driver.title)

# XPath patterns for each step
step1_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div/fieldset/label[4]/input"
# Select One Occupation for Multiple Industries

# List of required XPaths for step 2
# Each XPath Corresponds to Each Tech Occupation


step2_xpaths = [
    
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[2]/div/ul/li[3]/div/ul/li[2]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[2]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[2]/div/ul/li[2]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[3]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[4]/div/ul/li[1]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[4]/div/ul/li[2]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[5]/div/ul/li[1]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[5]/div/ul/li[2]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[5]/div/ul/li[3]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[5]/div/ul/li[4]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[6]/div/ul/li[1]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[6]/div/ul/li[2]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[6]/div/ul/li[3]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[6]/div/ul/li[4]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[6]/div/ul/li[5]/span",
    "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[4]/div/ul/li/div/ul/li[4]/div/ul/li[8]/div/ul/li[5]/span"
    
   
    # Add more XPaths as needed
]

# XPath patterns for the rest of the steps

# Step 3: To Select All Sectors in this list
# Step 4: To Select the Button Next
# Step 5: To Select All Industries in this list
# Step 6: To Select the Button Next
# Step 7: To Select All Data Types (Refer to Lines 9 - 24 for further details)
# Step 8: To Select the Button Next
# Step 9: To Select Output Format as Excel
# Step 10: To Select the Button Submit
step3_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[3]/div/div/div/div[4]/select/option[1]"
step4_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[3]/div/div/div/div[4]/button"
step5_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[4]/div/div/div/div[3]/div[2]/ul/li/div/div[1]/ul/li[1]/div/span[2]/input"
step6_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[4]/div/div/div/div[3]/button"
step7_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[5]/div/div/select/option[1]"
step8_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[5]/div/div/button"
step9_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[7]/div/div/div/select/option[2]"
step10_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[8]/button"

# Function to click on the element based on the given xpath
def click_element_by_xpath(driver, xpath):
    element = driver.find_element(By.XPATH, xpath)
    element.click()
    time.sleep(3)  # Add a short delay to allow the page to load

try:
    # Loop through the XPaths for step 2 and complete the cycle
    for i in range(len(step2_xpaths)):
        driver.get("https://data.bls.gov/oes/#/home")
        step2_xpath = step2_xpaths[i]

        # Click on elements for each step using the appropriate XPaths
        click_element_by_xpath(driver, step1_xpath)
        print("Step 1 done")
        time.sleep(3)
        click_element_by_xpath(driver, step2_xpath)
        print(f"Step 2 (XPath {i+1}) done")
        time.sleep(3)
        click_element_by_xpath(driver, step3_xpath)
        print("Step 3 done")
        time.sleep(3)
        click_element_by_xpath(driver, step4_xpath)
        print("Step 4 done")
        time.sleep(3)
        click_element_by_xpath(driver, step5_xpath)
        print("Step 5 done")
        time.sleep(3)
        click_element_by_xpath(driver, step6_xpath)
        print("Step 6 done")
        time.sleep(3)
        click_element_by_xpath(driver, step7_xpath)
        print("Step 7 done")
        time.sleep(3)
        click_element_by_xpath(driver, step8_xpath)
        print("Step 8 done")
        time.sleep(3)
        click_element_by_xpath(driver, step9_xpath)
        print("Step 9 done")
        time.sleep(3)
        click_element_by_xpath(driver, step10_xpath)
        print("Step 10 done")
        time.sleep(3)

    # After completing all cycles, wait for the Excel data to download
    time.sleep(3)
    print("All excel data download is completed, thank you")

finally:
    driver.close()
