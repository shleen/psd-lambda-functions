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

from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

SSOCs = [
  1221, 1222, 
  1330, 1349, 2122, 2123, 2152, 2153, 
  2166, 2431, 2433, 2511, 2512, 2514, 2515, 2519, 
  2521, 2522, 2523, 2524, 2529, 2641, 2642, 2651, 
  2654, 2656, 3114, 3440, 3511, 3512, 3514, 3521, 
  3522, 3523, 3620, 4132, 4315, 5142, 7421, 7422
]

def login(driver, wait):
  driver.get("https://labourinsight.lightcast.io/sgp")

  time.sleep(5)

  email_field = driver.find_element(By.ID, "loginEmail")
  email_field.click()
  email_field.send_keys(os.environ['BG_EMAIL'])

  password_field = driver.find_element(By.ID, "Password")
  password_field.click()
  password_field.send_keys(os.environ['BG_PASSWORD'])

  login_button = driver.find_element(By.ID, "submit")
  login_button.click()

def navigate_to_occupation_analysis(driver, actions, wait):
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

def get_occupation_analysis(driver, actions, wait):
  navigate_to_occupation_analysis(driver, actions, wait)

  for ssoc in SSOCs:
    while True:
      print('Occupation Analysis SSOC: {}'.format(ssoc))
      
      # Print time elapsed
      t1 = time.time()
      
      try:
        time.sleep(3)

        # This block first attempts to switch the input mode to SSOC. This will work when
        # the input pop up is already open. If not, an ElementClickInterceptedException will
        # be thrown. In this case, the except block will toggle open the pop up and then
        # switch the input mode to SSOC.
        
        # try:
        #   driver.find_element(By.XPATH, '//span[text()="Switch to SSOC"]').click()
        # except:
        #   # it was breaking trying to find "titleFilterSource"
        #   try:
        #     driver.find_element(By.XPATH, '//div[@id="titleFilterSource"]').click()
        #     driver.find_element(By.XPATH, '//span[text()="Switch to SSOC"]').click()
        #   except:
        #     # FIXME: breaking somewhere here
        #     print("give it more time")
        #     time.sleep(10)
        #     driver.find_element(By.XPATH, '//div[@id="titleFilterSource"]').click()
        #     driver.find_element(By.XPATH, '//span[text()="Switch to SSOC"]').click()

        try:
          driver.find_element(By.XPATH, '//span[text()="Switch to SSOC"]').click()
        except:
          try:
            driver.find_element(By.XPATH, '//div[@id="titleFilterSource"]').click()
            driver.find_element(By.XPATH, '//span[text()="Switch to SSOC"]').click()
          except NoSuchElementException:
            driver.save_screenshot('cannotclickmenu' + '.png')
            s3_client.upload_file('cannotclickmenu' + '.png', 'psd-dashboard-data', 'cannotclickmenu' + '.png')
            print("*** retry SSOC -- could not click menu ***")
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
            print('getting kicked out here')
            login(driver, wait)
            navigate_to_occupation_analysis(driver, actions, wait)
            continue
          break

        # if noDataPopup and display: block popup is found, break to iterate the next SSOC
        # when it is not found, we get an NoSuchElementException

        try:
          driver.find_element(By.XPATH, '//div[@id="noDataPopup" and @style="display: none;"]')
          # FIXME: not printing this
          print("there is data")
        except NoSuchElementException:
          driver.find_element(By.XPATH,
                            '//a[@class="dashboard-filter-reset"]').click()
          print("there is no data")
          break

        
        wait.until(
          EC.element_to_be_clickable(
            (By.XPATH, '//div[@id="Workforce-export-section"]')))
        driver.find_element(By.XPATH,
                            '//div[@id="Workforce-export-section"]').click()
        
        # FIXME: add time sleep here? but there's no error message meaning it's able to click
        #time.sleep(1)

        wait.until(
          EC.element_to_be_clickable(
            (By.XPATH, '//span[text()="Excel"]')))
        driver.find_element(By.XPATH, '//span[text()="Excel"]').click()

        time.sleep(5)

        file_name = "Occupation Analysis.xlsx"
        file_path = "/tmp/" + file_name

        # TODO: rewrite as try/except
        s3_client = boto3.client('s3')
        
        time_counter = 0

        print("before trying to wait")

        while not os.path.exists(file_path):
          print("file cannot be found \n waiting " + str(time_counter) +"s")
          # screenshot testing
          # driver.save_screenshot('notexist' + str(time_counter) + '.png')
          # s3_client.upload_file('notexist' + str(time_counter) + '.png', 'psd-dashboard-data', 'notexist' + str(time_counter) + '.png')
          time.sleep(1)
          time_counter += 1
          if time_counter > 20: 
            break

        print("after trying to wait")

        new_file_name = "Occupation Analysis_ssoc_" + str(ssoc) + ".xlsx"
        new_file_path = os.path.join("/tmp", new_file_name)
        try:
          shutil.move(file_path, new_file_path)
        except FileNotFoundError:
          print("*** retry SSOC -- could not save file ***")

          login(driver, wait)
          navigate_to_occupation_analysis(driver, actions, wait)

          continue

        # reset filter
        driver.find_element(By.XPATH,
                            '//a[@class="dashboard-filter-reset"]').click()

      except (ElementClickInterceptedException, NoSuchElementException):
        # for when kicked out
        print('getting kicked out')
        login(driver, wait)
        # for the stuff above the while loop
        navigate_to_occupation_analysis(driver, actions, wait)
        continue
      t2 = time.time()
      time_passed = t2 - t1
      print('Time passed: {}s'.format(time_passed))
      break
    

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

    # Add 'SSOC' column by extracting the ssoc from the filename
    skill_sheet['SSOC'] = file[-9:-5]

    # Drop 'Salary Premium' column
    skill_sheet.drop(labels=['Salary Premium'], axis=1, inplace=True)

    if not os.path.isfile('/tmp/Occupation Analysis Skills.csv'):
      skill_sheet.to_csv('/tmp/Occupation Analysis Skills.csv', header=True)
    else:
      skill_sheet.to_csv('/tmp/Occupation Analysis Skills.csv',
                          mode='a',
                          header=False)
  
  s3_client = boto3.client('s3')
  s3_client.upload_file('/tmp/Occupation Analysis Skills.csv', 'psd-dashboard-data', 'Occupation Analysis Skills.csv')

def handler(event=None, context=None):

  # assign size
  size = 0

  # assign folder path
  Folderpath = '/tmp'

  # get size
  for path, dirs, files in os.walk(Folderpath):
    for f in files:
      fp = os.path.join(path, f)
      size += os.stat(fp).st_size

  # display size	
  print("Folder size: " + str(size))


  start = time.time()
  load_dotenv()
  
  # try:
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

  wait = WebDriverWait(driver, 25)
  login(driver, wait)

  actions = ActionChains(driver)

  get_occupation_analysis(driver, actions, wait)
  consolidate_occupation_analysis_skills()

  # except Exception as e:
  #   print("Exception occured: ", e)

  end = time.time()
  time_elapsed = end - start
  print('Time elapsed: {}s'.format(time_elapsed))

# Uncomment for docker testing, comment for AWS lambda testing
handler()