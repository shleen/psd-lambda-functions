# Import libraries
import boto3
import os
import pandas as pd
import shutil
import time

from dotenv import load_dotenv
from queue import Queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from tempfile import mkdtemp

from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
  time.sleep(4)

  email_field = driver.find_element(By.ID, "loginEmail")
  email_field.click()
  email_field.send_keys(os.environ['BG_EMAIL'])

  password_field = driver.find_element(By.ID, "Password")
  password_field.click()
  password_field.send_keys(os.environ['BG_PASSWORD'])

  login_button = driver.find_element(By.ID, "submit")
  login_button.click()

# To download Excel sheet of 'Time Series' for each SSOC
def get_time_series(driver, wait):
  # Different Selenium actions to click buttons/menus and to input different values
  driver.find_element(By.XPATH,
                      '//a[contains(text(), "Create Reports")]').click()

  time.sleep(3)

  wait.until(
    EC.element_to_be_clickable((By.XPATH, '//div[@id="selectReportFocus"]')))

  time.sleep(3)

  driver.find_element(By.XPATH, '//div[@id="selectReportFocus"]').click()

  time.sleep(1)

  driver.find_element(By.XPATH,
                      '//a[@id="Time Series Analysis_anchor"]').click()

  driver.find_element(By.XPATH, '//div[@id="accordionOccupation"]').click()

  driver.find_element(By.XPATH, '//a[text()="SSOC Occupations"]').click()

  for ssoc in SSOCs:

    while True:
      print('Time Series SSOC: {}'.format(ssoc))
      
      # Print time elapsed
      t1 = time.time()
      
      try:
        wait.until(
          EC.element_to_be_clickable(
            (By.XPATH, '//input[@id="JTAndOccsOnetCode"]')))

        ssoc_input = driver.find_element(By.XPATH,
                                        '//input[@id="JTAndOccsOnetCode"]')
        ssoc_input.click()

        ssoc_input.send_keys(ssoc)

        time.sleep(1)
        driver.find_element(By.XPATH, f'//a[contains(text(), "{ssoc}")]').click()
        time.sleep(1)

        # Add SSOC to list
        add_button = driver.find_element(By.XPATH,
                                        '//button[@id="btn-add-soccode"]')
        add_button.click()

        try:
          driver.find_element(By.XPATH, '//button[@id="showReport"]').click()

          time.sleep(3)

          driver.find_element(
            By.XPATH, '//span[contains(text(), "Total Postings")]').click()

          driver.find_element(
            By.XPATH,
            '//span[contains(text(), "Top Occupations (SSOC)")]').click()

          driver.find_element(By.XPATH,
                              '//span[contains(text(), "5-D SSOC 2020")]').click()

          time.sleep(2)

          driver.find_element(
            By.XPATH,
            '//div[@id="liveSeriesSubPopupDataOccupation00"]/ul/li[2]').click()

          time.sleep(2)

          s3_client = boto3.client('s3')

          driver.find_element(By.XPATH,
                              '//span[contains(text(), "Annually")]').click()
          
          # Debug technique: Screenshot testing because of headless chrome
          # driver.save_screenshot('AfterClickAnnually.png')
          # s3_client.upload_file('AfterClickAnnually.png', 'psd-dashboard-data', 'AfterClickAnnually.png')          
          
          try:
            # Debug technique: Make "monthly" button red to see if the ID is correct
            # element = driver.find_element(
            #   By.XPATH, '//div[@id="liveSeriesIntervalPopup0"]/ul/li[2]')
            # driver.execute_script("arguments[0].setAttribute('style', 'background-color:DodgerBlue')", element)
            
            driver.find_element(
              # HTML starts from 1
              By.XPATH, '//div[@id="liveSeriesIntervalPopup0"]/ul/li[2]').click()
            
            time.sleep(3)

          except Exception as e:
            print(e)
        except NoSuchElementException:
          driver.find_element(By.XPATH,
                              '//button[@id="ParameterUpdateButton"]').click()
          
        time.sleep(3)

        wait.until(
          EC.element_to_be_clickable(
            (By.XPATH, '//div[@id="Workforce-export-section"]')))
        driver.find_element(By.XPATH,
                            '//div[@id="Workforce-export-section"]').click()
        driver.find_element(By.XPATH, '//span[text()="Excel"]').click()

        time.sleep(3)

        driver.find_element(
          By.XPATH, '//button[contains(text(), "Create/edit Report")]').click()
        time.sleep(1)

        occupation_accordion = driver.find_element(
          By.XPATH, '//div[@id="accordionOccupation"]')
        if 'expanded' not in occupation_accordion.get_attribute('class'):
          occupation_accordion.click()

        time.sleep(2)
        driver.find_element(By.XPATH, '//a[text()="SSOC Occupations"]').click()

        driver.find_element(By.XPATH, '//span[@class="combineImgText"]').click()

        file_path = '/tmp/Time Series Analysis.xlsx'
        
        # To ensure there is sufficient download time, up to 20s. 
        time_counter = 0
        # Searching in the /tmp folder
        while not os.path.exists(file_path):
          time.sleep(1)
          time_counter += 1
          if time_counter > 20:
            break
        
        # Saving and moving file so that there are no duplicate names
        new_file_name = "Time Series Analysis_ssoc_" + str(ssoc) + ".xlsx"
        new_file_path = os.path.join('/tmp', new_file_name)
        shutil.move(file_path, new_file_path)
      
      # To log back in when kicked out
      except ElementClickInterceptedException:
        login(driver, wait)
        continue

      # Print time elapsed for each SSOC
      t2 = time.time()
      time_passed = t2 - t1
      print('Time passed: {}s'.format(time_passed))
      break
  
  time.sleep(3)

# Consolidation is done after all the Excel sheets are downloaded. Therefore, deleting after downloading is not an option to save storage.
def consolidate_time_series_analysis():
  time_series_analysis_files = [
    file for file in os.listdir('/tmp/') if 'Time Series Analysis_ssoc_' in file
  ]

  columns = ['4D SSOC', '5D Job Title', 'Period', 'Job Postings']

  output = pd.DataFrame(columns=columns)

  for file in time_series_analysis_files:
    # Read 'Occupation Analysis' report
    data_sheet = pd.read_excel(f'/tmp/{file}', 'Data')
    
    # Drop unnamed column
    data_sheet.drop(labels=[c for c in data_sheet.columns if 'Unnamed' in c],
                    inplace=True,
                    axis=1)

    for i in range(1, len(data_sheet.columns)):
      for j in range(data_sheet.shape[0]):
        output.loc[len(output)] = [
          file[-9:-5], data_sheet.columns[i], data_sheet.iloc[j, 0],
          data_sheet.iloc[j, i]
        ]

  # Else, go into append mode to add the skill sheet of each SSOC
  if not os.path.isfile('/tmp/Time Series Analysis.csv'):
    output.to_csv('/tmp/Time Series Analysis.csv', header=True, index=False)
  else:
    output.to_csv('/tmp/Time Series Analysis.csv',
                  mode='a',
                  header=False,
                  index=False)

  # Upload and save the Excel file as 'time_series_analysis_{int(time.time())}.csv' on S3
  s3_client = boto3.client('s3')
  # s3_client.upload_file('/tmp/Time Series Analysis.csv', 'psd-dashboard-data', f'time_series_analysis_{int(time.time())}.csv')
  s3_client.upload_file('/tmp/Time Series Analysis.csv', 'psd-dashboard-data', f'Time Series Analysis {int(time.time())}.csv')

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
  print("Time Series V1")

  # Print size of files in temp folder
  size = 0
  Folderpath = '/tmp'
  for path, dirs, files in os.walk(Folderpath):
    for f in files:
      fp = os.path.join(path, f)
      size += os.stat(fp).st_size
  print("Folder size: " + str(size))

  wait = WebDriverWait(driver, 30)

  # Call the functions defined above
  login(driver, wait)
  get_time_series(driver, wait)
  consolidate_time_series_analysis()

  # Print total time elapsed
  end = time.time()
  time_elapsed = end - start
  print('Time elapsed: {}s'.format(time_elapsed))

# Uncomment for docker testing, comment for AWS lambda testing -- because AWS will call handler by default
# handler()