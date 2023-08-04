import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.service import Service
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time

import shutil

### XPath patterns for each step

# Select One Occupation for Multiple Industries
step1_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div/fieldset/label[4]/input"

## List of required XPaths for step 2

# Each XPath Corresponds to Each Tech Occupation, such as Computer and Information Systems Manager
step2_xpaths = [
    # Add more XPaths as needed
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
]

## XPath patterns for the rest of the steps

# Step 3: To Select All Sectors in this list
step3_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[3]/div/div/div/div[4]/select/option[1]"

# Step 4: To Select the Button Next
step4_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[3]/div/div/div/div[4]/button"

# Step 5: To Select All Industries in this list
step5_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[4]/div/div/div/div[3]/div[2]/ul/li/div/div[1]/ul/li[1]/div/span[2]/input"

# Step 6: To Select the Button Next
step6_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[4]/div/div/div/div[3]/button"

# Step 7: To Select All Data Types (Refer to Lines 9 - 24 for further details)
step7_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[5]/div/div/select/option[1]"

# Step 8: To Select the Button Next
step8_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[5]/div/div/button"

# Step 9: To Select Output Format as Excel
step9_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[7]/div/div/div/select/option[2]"

# Step 10: To Select the Button Submit
step10_xpath = "/html/body/div[2]/div/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[3]/div[8]/button"

# Function to click on the element based on the given xpath
def click_element_by_xpath(driver, xpath):
    element = driver.find_element(By.XPATH, xpath)
    element.click()
    time.sleep(3)  # Add a short delay to allow the page to load

# AWS Lambda calls the handler() function by default. The functions that we want to invoke must be in order in handler(). Thus, we don't need to call handler() in
# AWS Lambda, but we have to when testing in Docker (because Docker does not call handler() by default). 
def handler(event=None, context=None):
    # driver = webdriver.Firefox("/opt/geckodriver", options=options)
    # options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

    options = Options()
    # options = webdriver.FirefoxOptions()
    print("failing before binary location")
    
    from selenium.webdriver.firefox.service import Service

    geckodriver_path = Service('/opt/firefox/firefox')

    # FIXME: Think this is the issue? is it geckodriver or firefox here. think it should be firefox but something is wrong with teh downloadde firefox file
    # options.binary_location = '/opt/firefox/firefox'
    print("failing before driver")
    
    # binary = FirefoxBinary('/opt/firefox/firefox')
    driver = webdriver.Firefox(service = geckodriver_path, options=options)
    print("failing after driver")

    driver.get("https://data.bls.gov/oes/#/home")
    print(driver.title)

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

            # Rename and move file
            file_path = '/tmp/OES_Report.xlsx'
            new_file_name = "OES Report " + str(i) + ".xlsx"
            new_file_path = os.path.join('/tmp', new_file_name)
            shutil.move(file_path, new_file_path)

        # After completing all cycles, wait for the Excel data to download
        time.sleep(3)
        print("All excel data download is completed, thank you")

    finally:
        driver.close()

handler()



