# Motivation: The data extracted from LabourInsights regard skills on the demand-side. This can be contrasted with skills on the supply-side (e.g. what 
# skills do the graduates coming out of University possess), allowing us to determine the skill gap. The SSOC data that we are extracting from are the SSOCs of 
# identified tech jobs that are indicative of the hiring tech landscape in Singapore. These SSOCs are obtained from the manpower survey.

# This script is currently deployed on AWS Lambda. It's purpose is to scrape "Occupation Analysis" information from LabourInsights (Burning Glass)
# and to upload it on Amazon S3 as an Excel file -- object storage service that stores data as objects.
# To call/invoke this script, we use a Workato recipe with a scheduler trigger. At the indicated timing or frequency, this script would be ran on AWS
# and the information would be uploaded on S3.
# A separate Workato recipe scans for new files on S3 in specified intervals and would email the Excel file to the preferred email once it has been fetched.

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

from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# List of SSOCs to extract data from
SSOCs = [
  1221, 1222, 
  1330, 1349, 2122, 2123, 2152, 2153, 
  2166, 2431, 2433, 2511, 2512, 2514, 2515, 2519, 
  2521, 2522, 2523, 2524, 2529, 2641, 2642, 2651, 
  2654, 2656, 3114, 3440, 3511, 3512, 3514, 3521, 
  3522, 3523, 3620, 4132, 4315, 5142, 7421, 7422
]

# Automate the login process. It is defined as a stand-alone function because we want to call the login function when there is a force logout on LabourInsights
def login(driver, wait):
  driver.get("https://labourinsight.lightcast.io/sgp")

  # to delay the next step. if there is no delay, the chrome driver would not have enough time to load the element (in this case an element with ID = "loginEmail").
  # thus, an exception would be raised (NoSuchElementException), breaking the script. in this case, we don't use error handling (try; except) because a simple 
  # time.sleep() would suffice. there will be more examples of error handling below.
  time.sleep(5)

  email_field = driver.find_element(By.ID, "loginEmail")
  email_field.click()
  email_field.send_keys(os.environ['BG_EMAIL'])

  password_field = driver.find_element(By.ID, "Password")
  password_field.click()
  password_field.send_keys(os.environ['BG_PASSWORD'])

  login_button = driver.find_element(By.ID, "submit")
  login_button.click()

# To go to the page of "Occupation Analysis"
def navigate_to_occupation_analysis(driver, actions, wait):
  # delaying for the same purpose as time.sleep() that is used in the function above. 
  # advantage of using this is that it will waste less time as it stops waiting once element is found. 
  # disadvantage of this is that some developers unhide buttons just by changing the CSS. this means that the button is always there to the computer but just becomes
  # visible to the human eye. hence, it will not wait in this scenario.
  wait.until(
    EC.element_to_be_clickable(
      (By.XPATH, '//*[contains(text(), "Occupation Analysis")]')))
  skill_spotlight = driver.find_element(
    By.XPATH, '//*[contains(text(), "Occupation Analysis")]')
  actions.move_to_element(skill_spotlight).click().perform()

  wait.until(
    EC.element_to_be_clickable(
      (By.XPATH, '//button[contains(text(), "Start")]')))
  start_button = driver.find_element(By.XPATH,
                                     '//button[contains(text(), "Start")]')
  start_button.click()

# To download Excel sheet of 'Occupation Analysis' for each SSOC
def get_occupation_analysis(driver, actions, wait):
  navigate_to_occupation_analysis(driver, actions, wait)

  for ssoc in SSOCs:
    while True:
      print('Occupation Analysis SSOC: {}'.format(ssoc))
      t1 = time.time()
      
      try:
        time.sleep(3)

        # This block first attempts to switch the input mode to SSOC. This will work when the input pop up is already open. If not, an 
        # ElementClickInterceptedException will be thrown. In this case, the except block will toggle open the pop up and then switch the input mode to SSOC.
        try:
          driver.find_element(By.XPATH, '//span[text()="Switch to SSOC"]').click()
        except:
          try:
            driver.find_element(By.XPATH, '//div[@id="titleFilterSource"]').click()
            driver.find_element(By.XPATH, '//span[text()="Switch to SSOC"]').click()
          except NoSuchElementException:
            # Screenshot testing if it catches the exception. Given that AWS Lambda is only able to run Chrome headless, we are not able to see what goes on when
            # Selenium is tries to click buttons. Hence, Screenshot testing is needed for us to see what actually goes on.
            driver.save_screenshot('cannotclickmenu' + '.png')
            s3_client.upload_file('cannotclickmenu' + '.png', 'psd-dashboard-data', 'cannotclickmenu' + '.png')
            print("*** Retry SSOC -- Could not click menu ***")
            continue

        ssoc_input = driver.find_element(By.XPATH,
                                        '//input[@id="selectAnzscoOccupation"]')
        ssoc_input.click()

        ssoc_input.send_keys(ssoc)

        time.sleep(1)

        driver.find_element(By.XPATH,
                            f'//li[contains(text(), "({ssoc})")]').click()

        driver.find_element(By.XPATH, '//button[text()="Apply Filters"]').click()
        
        try:
          wait.until(
            EC.element_to_be_clickable(
              (By.XPATH, '//div[@id="Workforce-export-section"]')))
        except:
          try:
            driver.find_element(By.XPATH, '//div[@id="noDataPopup"]//span[@data-bind="click: closeNoDataPopup"]').click()
            time.sleep(1)
            driver.find_element(By.XPATH,
                              '//a[@class="dashboard-filter-reset"]').click()
          except:
            # When LabourInsights force logouts, we try to log back in and continue from the same SSOC. E.g. If another user uses the same account, the older session
            # will expire.
            print('getting kicked out here')
            login(driver, wait)
            navigate_to_occupation_analysis(driver, actions, wait)
            continue
          break

        # If "noDataPopup" and "display: block popup" is not found, we get an NoSuchElementException. Thus, we break and go to the next SSOC. E.g. SSOC 3523 is empty.
        try:
          driver.find_element(By.XPATH, '//div[@id="noDataPopup" and @style="display: none;"]')
        except NoSuchElementException:
          driver.find_element(By.XPATH,
                            '//a[@class="dashboard-filter-reset"]').click()
          break
        
        # To ensure sufficient time is given to click the menus. It was prone to breaking here.
        wait.until(
          EC.element_to_be_clickable(
            (By.XPATH, '//div[@id="Workforce-export-section"]')))
        driver.find_element(By.XPATH,
                            '//div[@id="Workforce-export-section"]').click()
        wait.until(
          EC.element_to_be_clickable(
            (By.XPATH, '//span[text()="Excel"]')))
        driver.find_element(By.XPATH, '//span[text()="Excel"]').click()

        # Additional layer of safety to ensure sufficient time is given.
        time.sleep(5)

        file_name = "Occupation Analysis.xlsx"
        file_path = "/tmp/" + file_name

        # A low-level client representing Amazon Simple Storage Service (S3)
        s3_client = boto3.client('s3')
        
        # To ensure there is sufficient download time, up to 20s. 
        time_counter = 0
        while not os.path.exists(file_path):
          print("File cannot be found. Waiting: " + str(time_counter) +"s")
          # screenshot testing
          # driver.save_screenshot('notexist' + str(time_counter) + '.png')
          # s3_client.upload_file('notexist' + str(time_counter) + '.png', 'psd-dashboard-data', 'notexist' + str(time_counter) + '.png')
          time.sleep(1)
          time_counter += 1
          if time_counter > 20: 
            break

        # Downloading, renaming and moving the Excel file
        new_file_name = "Occupation Analysis_ssoc_" + str(ssoc) + ".xlsx"
        new_file_path = os.path.join("/tmp", new_file_name)
        try:
          shutil.move(file_path, new_file_path)
        except FileNotFoundError:
          # If it still fails to download after 20s, we will retry the same SSOC.
          print("*** Retry SSOC -- Could not save file ***")
          login(driver, wait)
          navigate_to_occupation_analysis(driver, actions, wait)
          continue

        # Reset filter
        driver.find_element(By.XPATH,
                            '//a[@class="dashboard-filter-reset"]').click()

      # To log back in when kicked out
      except (ElementClickInterceptedException, NoSuchElementException):
        print('getting kicked out')
        login(driver, wait)
        navigate_to_occupation_analysis(driver, actions, wait)
        continue

      # Print time elapsed for each SSOC
      t2 = time.time()
      time_passed = t2 - t1
      print('Time passed: {}s'.format(time_passed))
      break

# Consolidation is done after all the Excel sheets are downloaded. Therefore, deleting after downloading is not an option to save storage.
def consolidate_occupation_analysis_skills():
  occupation_analysis_files = [
    file for file in os.listdir("/tmp") if 'Occupation Analysis_ssoc_' in file
  ]

  columns = [
    'SSOC', 'Skill', 'Skill Type', 'Description',
    'Job Postings Requesting (Last 12 Months)', 'Projected Growth (2 Years)'
  ]
  for file in occupation_analysis_files:
    # Read 'Occupation Analysis' report
    skill_sheet = pd.read_excel('/tmp/' + file, 'Skills', skiprows=7)

    # Add 'SSOC' column by extracting the ssoc from the filename. [-9:-5] refers to the last few characters of the file name that corresponds to the SSOC number.
    skill_sheet['SSOC'] = file[-9:-5]

    # Drop 'Salary Premium' column
    skill_sheet.drop(labels=['Salary Premium'], axis=1, inplace=True)

    # Else, go into append mode to add the skill sheet of each SSOC
    if not os.path.isfile('/tmp/Occupation Analysis Skills.csv'):
      skill_sheet.to_csv('/tmp/Occupation Analysis Skills.csv', header=True)
    else:
      skill_sheet.to_csv('/tmp/Occupation Analysis Skills.csv', mode='a', header=False)
  
  # Upload and save the Excel file as 'Occupation Analysis Skills.csv' on S3
  s3_client = boto3.client('s3')
  timestamp = time.time()
  value = datetime.datetime.fromtimestamp(timestamp)
  human_time = value.strftime('%Y-%m-%d ') + str((int(value.strftime('%H'))+8)%24) + value.strftime('%M')
  s3_client.upload_file('/tmp/Occupation Analysis Skills.csv', 'psd-dashboard-data', f'Occupation Analysis Skills {human_time}.csv')

# AWS Lambda calls the handler() function by default. The functions that we want to invoke must be in order in handler(). Thus, we don't need to call handler() in
# AWS Lambda, but we have to when testing in Docker (because Docker does not call handler() by default).
def handler(event=None, context=None):

  start = time.time()
  # Import API keys
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
  for root, dirs, files in os.walk('/tmp'):
    for f in files:
        os.unlink(os.path.join(root, f))
    for d in dirs:
        shutil.rmtree(os.path.join(root, d))

  # Print version
  print("Occupation Analysis V1")

  # Print size of files in temp folder
  size = 0
  Folderpath = '/tmp'
  for path, dirs, files in os.walk(Folderpath):
    for f in files:
      fp = os.path.join(path, f)
      size += os.stat(fp).st_size
  print("Folder size: " + str(size))

  wait = WebDriverWait(driver, 25)
  
  # Call the functions defined above
  login(driver, wait)
  actions = ActionChains(driver)
  get_occupation_analysis(driver, actions, wait)
  consolidate_occupation_analysis_skills()

  # Print total time elapsed
  end = time.time()
  time_elapsed = end - start
  print('Time elapsed: {}s'.format(time_elapsed))

# Uncomment for docker testing, comment for AWS lambda testing -- because AWS will call handler by default
# handler()