# Import libraries
import boto3
import os
import pandas as pd
import shutil
import time
import datetime

from dotenv import load_dotenv
from queue import Queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from tempfile import mkdtemp

from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    # Add a short delay to allow the page to load
    time.sleep(3)  

def get_us_bls(driver):
    # Loop through the XPaths for step 2 and complete the cycle
    for i in range(len(step2_xpaths)):
        driver.get("https://data.bls.gov/oes/#/home")
        step2_xpath = step2_xpaths[i]

        # Give webpage time to load
        time.sleep(3)

        # Click on elements for each step using the appropriate XPaths
        click_element_by_xpath(driver, step1_xpath)
        print("Step 1 done")
        # time.sleep(3)

        click_element_by_xpath(driver, step2_xpath)
        print(f"Step 2 (XPath {i+1}) done")
        # time.sleep(3)

        click_element_by_xpath(driver, step3_xpath)
        print("Step 3 done")
        # time.sleep(3)

        click_element_by_xpath(driver, step4_xpath)
        print("Step 4 done")
        # time.sleep(3)

        click_element_by_xpath(driver, step5_xpath)
        print("Step 5 done")
        # time.sleep(3)

        click_element_by_xpath(driver, step6_xpath)
        print("Step 6 done")
        # time.sleep(3)

        click_element_by_xpath(driver, step7_xpath)
        print("Step 7 done")
        # time.sleep(3)

        click_element_by_xpath(driver, step8_xpath)
        print("Step 8 done")
        # time.sleep(3)

        click_element_by_xpath(driver, step9_xpath)
        print("Step 9 done")
        # time.sleep(3)

        click_element_by_xpath(driver, step10_xpath)
        print("Step 10 done")

        # Longer time.sleep to ensure file download
        time.sleep(5)

        # Rename and move file
        file_path = '/tmp/OES_Report.xlsx'
        # Give each file a unique name such that they don't overwrite.
        new_file_name = "OES Report " + str(i) + ".xlsx"
        new_file_path = os.path.join('/tmp', new_file_name)
        shutil.move(file_path, new_file_path)

    # After completing all cycles, wait for the Excel data to download
    time.sleep(3)
    print("All excel data download is completed, thank you")

def consolidate_us_bls():
    # Path to the folder containing your Excel files
    input_folder = r"/tmp/"

    # Path to the output Excel file where you want to append the data
    output_file = r"/tmp/US BLS.csv"

    # Get a list of all .xlsx files in the input folder (/tmp/). Does not look into S3.
    input_files = [f for f in os.listdir(input_folder) if 'OES Report' in f]

    # Initialize an empty list to store DataFrames
    data_frames = []

    # Loop through each input file and read it as a DataFrame
    for file in input_files:
        file_path = os.path.join(input_folder, file)
        df = pd.read_excel(file_path, header=None)  # Read without header
        data_frames.append(df)

    # Concatenate all DataFrames in the list into a single DataFrame
    combined_data = pd.concat(data_frames, ignore_index=True)

    # Write the combined data to the output Excel file without column headers
    combined_data.to_csv(output_file, index=False, header=False)

    print("Data appended and saved to", output_file)

    # Upload the Excel file on S3
    s3_client = boto3.client('s3')
    timestamp = time.time()
    value = datetime.datetime.fromtimestamp(timestamp)
    human_time = value.strftime('%Y-%m-%d ') + str((int(value.strftime('%H'))+8)%24) + value.strftime('%M')
    s3_client.upload_file('/tmp/US BLS.csv', 'psd-dashboard-data', f'US BLS {human_time}.csv')

# AWS Lambda calls the handler() function by default. The functions that we want to invoke must be in order in handler(). Thus, we don't need to call handler() in
# AWS Lambda, but we have to when testing in Docker (because Docker does not call handler() by default). 
def handler(event=None, context=None):
    # load API Keys
    load_dotenv()

    # Configure ChromeDriver
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
    prefs = {"profile.default_content_settings.popups": 0,    
            "download.default_directory":r"/tmp",
            "download.prompt_for_download": False,
            "directory_upgrade": True}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("/opt/chromedriver", options=options)

    # Delete contents of temp folder
    # TODO: haven't tested if this breaks the code
    for root, dirs, files in os.walk('/tmp'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

    driver.get("https://data.bls.gov/oes/#/home")
    print(driver.title)

    get_us_bls(driver)
    
    consolidate_us_bls()

# handler()