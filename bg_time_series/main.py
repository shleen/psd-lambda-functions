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

# SSOCs = [
#   1221, 1222, 1330, 1349, 2122, 2123, 2152, 2153, 2166, 2431, 2433, 2511, 2512,
#   2514, 2515, 2519, 2521, 2522, 2523, 2524, 2529, 2641, 2642, 2651, 2654, 2656,
#   3114, 3440, 3511, 3512, 3514, 3521, 3522, 3523, 3620, 4132, 4315, 5142, 7421,
#   7422
# ]

SSOCs = [
  1221, 1222, 1330, 1349, 2122, 2123, 2152, 2153, 2166, 2431, 2433, 2511, 2512 ]

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

def consolidate_time_series_analysis():
  time_series_analysis_files = [
    file for file in os.listdir('/tmp/') if 'Time Series Analysis_ssoc_' in file
  ]

  columns = ['4D SSOC', '5D Job Title', 'Period', 'Job Postings']
  for file in time_series_analysis_files:
    data_sheet = pd.read_excel(f'/tmp/{file}', 'Data')
    data_sheet.drop(labels=[c for c in data_sheet.columns if 'Unnamed' in c],
                    inplace=True,
                    axis=1)

    output = pd.DataFrame(columns=columns)
    for i in range(1, len(data_sheet.columns)):
      for j in range(data_sheet.shape[0]):
        output.loc[len(output)] = [
          file[-9:-5], data_sheet.columns[i], data_sheet.iloc[j, 0],
          data_sheet.iloc[j, i]
        ]

    if not os.path.isfile('/tmp/Time Series Analysis.csv'):
      output.to_csv('/tmp/Time Series Analysis.csv', header=True, index=False)
    else:
      output.to_csv('/tmp/Time Series Analysis.csv',
                    mode='a',
                    header=False,
                    index=False)

    s3_client = boto3.client('s3')
    s3_client.upload_file('/tmp/Time Series Analysis.csv', 'psd-dashboard-data', f'time_series_analysis_{int(time.time())}.xlsx')


def get_time_series(driver, wait):
  driver.find_element(By.XPATH,
                      '//a[contains(text(), "Create Reports")]').click()

  time.sleep(3)

  wait.until(
    EC.element_to_be_clickable((By.XPATH, '//div[@id="selectReportFocus"]')))

  time.sleep(5)

  driver.find_element(By.XPATH, '//div[@id="selectReportFocus"]').click()

  time.sleep(1)

  driver.find_element(By.XPATH,
                      '//a[@id="Time Series Analysis_anchor"]').click()

  driver.find_element(By.XPATH, '//div[@id="accordionOccupation"]').click()

  driver.find_element(By.XPATH, '//a[text()="SSOC Occupations"]').click()

  for ssoc in SSOCs:
    while True:
      try:
        ssoc_input = driver.find_element(By.XPATH,
                                        '//input[@id="JTAndOccsOnetCode"]')
        ssoc_input.click()  # give focus

        ssoc_input.send_keys(ssoc)

        time.sleep(1)
        driver.find_element(By.XPATH, f'//a[contains(text(), "{ssoc}")]').click()
        time.sleep(1)

        # add to list
        add_button = driver.find_element(By.XPATH,
                                        '//button[@id="btn-add-soccode"]')
        add_button.click()

        try:
          driver.find_element(By.XPATH, '//button[@id="showReport"]').click()

          time.sleep(3)
        except NoSuchElementException:
          driver.find_element(By.XPATH,
                              '//button[@id="ParameterUpdateButton"]').click()
        finally:
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

          driver.find_element(By.XPATH,
                              '//span[contains(text(), "Annually")]').click()

          time.sleep(2)

          driver.find_element(
            By.XPATH, '//div[@id="liveSeriesIntervalPopup0"]/ul/li[1]').click()

        time.sleep(3)

        wait.until(
          EC.element_to_be_clickable(
            (By.XPATH, '//div[@id="Workforce-export-section"]')))
        driver.find_element(By.XPATH,
                            '//div[@id="Workforce-export-section"]').click()
        driver.find_element(By.XPATH, '//span[text()="Excel"]').click()

        time.sleep(5)

        driver.find_element(
          By.XPATH, '//button[contains(text(), "Create/edit Report")]').click()
        time.sleep(1)

        occupation_accordion = driver.find_element(
          By.XPATH, '//div[@id="accordionOccupation"]')
        if 'expanded' not in occupation_accordion.get_attribute('class'):
          occupation_accordion.click()

        time.sleep(1)
        driver.find_element(By.XPATH, '//a[text()="SSOC Occupations"]').click()

        driver.find_element(By.XPATH, '//span[@class="combineImgText"]').click()

        file_path = '/tmp/Time Series Analysis.xlsx'
        time_counter = 0
        while not os.path.exists(file_path):
          time.sleep(1)
          time_counter += 1
          if time_counter > 20:
            break
        
        new_file_name = "Time Series Analysis_ssoc_" + str(ssoc) + ".xlsx"
        new_file_path = os.path.join('/tmp', new_file_name)
        shutil.move(file_path, new_file_path)
      except ElementClickInterceptedException:
        continue
      break
  
  time.sleep(5)

  
def handler(event=None, context=None):
  load_dotenv()
  
  try:
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

    wait = WebDriverWait(driver, 10)
    login(driver, wait)

    get_time_series(driver, wait)
    consolidate_time_series_analysis()

  except Exception as e:
    print("Exception occured: ", e)
