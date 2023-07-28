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

# define wait times for webscrape to run
def wait():
    time.sleep(3)
def long_wait():
    time.sleep(5)

# click on accept cookies button
def close_cookie(driver):
    try:
        close_btn = driver.find_element(By.XPATH, "//div[@class='eu-cookie-compliance-buttons']")
        close_btn.click()
        wait()
    except:
        print("Cookie button not found")

def handler(event=None, context=None):
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
    chrome = webdriver.Chrome("/opt/chromedriver", options=options)
    chrome.get("https://www.topuniversities.com/university-rankings/university-subject-rankings/{year}/computer-science-information-systems?&tab=indicators&sort_by=overallscore&order_by=desc")
    chrome.maximize_window()
    long_wait()
    close_cookie(chrome)
    data = chrome.find_elements(By.XPATH, "//*[@class='td-wrap-in']")
    long_wait()
    print(len(data))
    
    # for i in range(len(data)):
    #     print(i, data[i].text)
    print("hello world")

# def handler(event=None, context=None):
#     options = webdriver.ChromeOptions()
#     options.binary_location = '/opt/chrome/chrome'
#     options.add_argument('--headless')
#     options.add_argument('--no-sandbox')
#     options.add_argument("--disable-gpu")
#     options.add_argument("--window-size=1280x1696")
#     options.add_argument("--single-process")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-dev-tools")
#     options.add_argument("--no-zygote")
#     options.add_argument(f"--user-data-dir={mkdtemp()}")
#     options.add_argument(f"--data-path={mkdtemp()}")
#     options.add_argument(f"--disk-cache-dir={mkdtemp()}")
#     options.add_argument("--remote-debugging-port=9222")
#     chrome = webdriver.Chrome("/opt/chromedriver",
#                               options=options)
#     chrome.get("https://example.com/")
#     return chrome.find_element(by=By.XPATH, value="//html").text

handler()