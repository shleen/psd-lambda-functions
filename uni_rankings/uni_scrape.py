#!/usr/bin/env python
# coding: utf-8

# In[1]:

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import pprint
import datetime as dt
year = dt.datetime.now().year
def wait():
    time.sleep(3)
def long_wait():
    time.sleep(5)
def close_cookie(driver):
    try:
        close_btn = driver.find_element(By.XPATH, "//div[@class='eu-cookie-compliance-buttons']")
        close_btn.click()
        wait()
    except:
        print("Cookie button not found")


# In[2]:


def setup(year):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    prefs = {"download.default_directory": ""}
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://www.topuniversities.com/university-rankings/university-subject-rankings/{year}/computer-science-information-systems?&tab=indicators&sort_by=overallscore&order_by=desc")
    driver.maximize_window()
    long_wait()
    close_cookie(driver)
    
    # Check if the page contains the "Coming Soon!" error message
    if 'Coming Soon!' in driver.page_source:
        year -= 1
        driver.quit()
        return setup(year)  # Recursively call setup() with the decremented year
    
    return driver


# In[3]:


def click_load_more(driver):
    while True:
        try:
            # Check if the "No data found" message is present
            time.sleep(5)
            no_data_msg = driver.find_element(By.XPATH, "//div[contains(text(), 'No data found on applied filters')]")
            break  # Stop clicking the "Load More" button if the message is found
        except NoSuchElementException:
            pass

        try:
            load_more_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'loadmorebutton') and contains(text(), 'Load More')]")
            driver.execute_script("arguments[0].scrollIntoView();", load_more_btn)
            driver.execute_script("arguments[0].click();", load_more_btn)
            wait()
        except NoSuchElementException:
            # If the "Load More" button is not found, break the loop
            break

driver = setup(year)
click_load_more(driver)


# In[4]:


def table_click_right(driver):
  right_arrow = driver.find_elements(By.XPATH, "//span[@direction='right']")
  right_arrow[0].click()
  wait()
    
def extract_location(driver):
    locations = driver.find_elements(By.XPATH, "//div[contains(@class, 'location')]")
    location_data = []
    for location in locations:
        location_text = location.text.strip()
        if location_text:
            location_data.append(location_text)
    return location_data



######################################
# setting up dataframe of results #
######################################
df_columns = ["Country", "University", "QS Citations per Paper"]
df = pd.DataFrame(columns=df_columns)
######################################
# running webscrape #
######################################

time.sleep(20)


# In[5]:


data = driver.find_elements(By.XPATH, "//*[@class='td-wrap-in']")
for i in range(len(data)):
    print(i, data[i].text)


# In[6]:


schools_data = list()
for i in range(1, len(data), 8):
    schools_data.append(data[i].text)
schools_data


# In[7]:


table_click_right(driver)


# In[8]:


AR_data = list()
for i in range(3, len(data), 8):
    AR_data.append(data[i].text)
AR_data


# In[9]:


ER_data = list()
for i in range(4, len(data), 8):
    ER_data.append(data[i].text)
ER_data


# In[10]:


citations_data = list()
for i in range(5, len(data), 8):
    citations_data.append(data[i].text)
citations_data


# In[11]:


location_data = extract_location(driver)
print(location_data)


# In[12]:


df["Country"] = location_data
df["University"] = schools_data
df["QS Citations per Paper"] = citations_data
df["QS Academic Reputation"] = AR_data
df["QS Employer Reputation"] = ER_data


# In[13]:


df


# In[14]:


city_list = []
country_list = []

for location in location_data:
    # Check if the location contains a comma
    if ',' in location:
        # Split the string at the comma
        split_location = location.split(',')

        # Remove leading and trailing whitespaces from the city and country
        city = split_location[0].strip()
        country = split_location[1].strip()

        city_list.append(city)
        country_list.append(country)
    else:
        city_list.append(location)
        country_list.append(None)
print(city_list)
print(country_list)


# In[15]:


# Replace the values in the "Country" column
df['Country'] = df['Country'].replace("China", "China (Mainland)")
df['Country'] = country_list
df = df[['University','Country', "QS Citations per Paper", 
         "QS Academic Reputation", "QS Employer Reputation"]]
df_qs = df


# In[ ]:





# In[ ]:





# In[16]:


df_qs.to_excel('QS.xlsx')


# In[17]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

import time
import pandas as pd
import numpy as np
import pprint

def wait():
    time.sleep(3)

def long_wait():
    time.sleep(5)

# Set up chromedriver
def setup(year):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')

    prefs = {"download.default_directory": ""}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://www.timeshighereducation.com/world-university-rankings/{year}/subject-ranking/computer-science#!/length/-1/sort_by/rank/sort_order/asc/cols/stats")
    driver.maximize_window()
    long_wait()

    # Check if the page displays the error message
    if "Sorry, we couldn't find that page. Try searching instead." in driver.page_source:
        year -= 1
        driver.quit()
        return setup(year)  # Recursively call setup() with the decremented year

    return driver

# Click on "Scores" button
def table_click_scores(driver):
  scores = driver.find_elements(By.XPATH, "//label[contains(@for, 'scores')]")
  scores[0].click()
  wait()

# Launch chromedriver
driver = setup(year)

# Show scores menu
table_click_scores(driver)


# extract function not even needed
def extract(df, driver):
  table_data = driver.find_element(By.XPATH, "//div[contains(@class, 'pane-content')]")
  table_rows = table_data.find_elements(By.XPATH, "//tr[contains(@role, 'row')]")
  for i in range(2, len(table_rows) - 1, 2):
    row = table_rows[i]
    data = row.find_element(By.XPATH, "/")
    for d in data:
      print(d.text)

######################################
# setting up dataframe of results #
######################################
df_columns = ["University", "Country", "Citations","Research", "Teaching"]
df = pd.DataFrame(columns=df_columns)
######################################
# running webscrape #
######################################

time.sleep(20)

# Scraping Rank, University Name & Country
df_rank = driver.find_elements(By.XPATH, "//td[contains(@class, 'rank sorting_1 sorting_2')]")
rank_data = list()
for i in range(len(df_rank)):
    rank_data.append(df_rank[i].text)


df_name = driver.find_elements(By.XPATH, "//*[contains(@class, 'ranking-institution-title')]")
name_data = list()
for i in range(len(df_name)):
    name_data.append(df_name[i].text)

df_country = driver.find_elements(By.XPATH, "//div/span")
country_data = list()
for i in range(len(df_country)):
    country_data.append(df_country[i].text)

# # Scraping all the Scores
# df_overall = driver.find_elements(By.XPATH, "//td[contains(@class, 'scores overall-score')]")
# overall_data = list()
# for i in range(len(df_overall)):
#     overall_data.append(df_overall[i].text)

df_citations = driver.find_elements(By.XPATH, "//td[contains(@class, 'scores citations-score')]")
citations_data = list()
for i in range(len(df_citations)):
    citations_data.append(df_citations[i].text)

# df_industry_income = driver.find_elements(By.XPATH, "//td[contains(@class, 'scores industry_income-score')]")
# industry_income_data = list()
# for i in range(len(df_industry_income)):
#     industry_income_data.append(df_industry_income[i].text)

# df_international_outlook = driver.find_elements(By.XPATH, "//td[contains(@class, 'scores international_outlook-score')]")
# international_outlook_data = list()
# for i in range(len(df_international_outlook)):
#     international_outlook_data.append(df_international_outlook[i].text)

df_research = driver.find_elements(By.XPATH, "//td[contains(@class, 'scores research-score')]")
research_data = list()
for i in range(len(df_research)):
    research_data.append(df_research[i].text)

df_teaching = driver.find_elements(By.XPATH, "//td[contains(@class, 'scores teaching-score')]")
teaching_data = list()
for i in range(len(df_teaching)):
    teaching_data.append(df_teaching[i].text)

# Adding data to Dataframe
# df["Rank"] = rank_data
df["University"] = name_data
df["Country"] = country_data
# df["Overall"] = overall_data
df["Citations"] = citations_data
# df["Industry Income"] = industry_income_data
# df["International Outlook"] = international_outlook_data
df["Research"] = research_data
df["Teaching"] = teaching_data

print(df)
df_the = df
# Exporting Dataframe as excel sheet
df_the.to_excel('THE_scrape.xlsx')


# In[18]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
import pprint
import itertools

def wait():
    time.sleep(3)
def long_wait():
    time.sleep(5)

        
def click_cnci(driver):
    try:
        button = driver.find_element(By.XPATH, '//*[@id="content-box"]//th[5]//img')
        button.click()
        long_wait()
        cnci = driver.find_element(By.XPATH, '//li[text()="CNCI"]')
        cnci.click()
        wait()
    except Exception as e:
        print("cnci button not found", e)

def click_top(driver):
    try:
        button = driver.find_element(By.XPATH, '//*[@id="content-box"]//th[5]//img')
        button.click()
        long_wait()
        top = driver.find_element(By.XPATH, '//li[text()="TOP"]')
        top.click()
        wait()
    except Exception as e:
        print("top button not found", e)
        
# def click_award(driver):
#     try:
#         button = driver.find_element(By.XPATH, '//*[@id="content-box"]//th[5]//img')
#         button.click()
#         long_wait()
#         top = driver.find_element(By.XPATH, '//li[text()="AWARD"]')
#         top.click()
#         wait()
#     except Exception as e:
#         print("award button not found", e) 


# In[19]:


def setup(year):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    prefs = {"download.default_directory": ""}
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://www.shanghairanking.com/rankings/gras/{year}/RS0210")
    driver.maximize_window()
    long_wait()
    
    # Check if the page is inaccessible
    if "Sorry, the page is inaccessible" in driver.page_source:
        year -= 1
        driver.quit()
        return setup(year)  # Recursively call setup() with the decremented year
    
    return driver

df_columns = ["University", "CNCI", "TOP"]
df = pd.DataFrame(columns=df_columns)
driver = setup(year)


# In[20]:


def extract_names(driver):
    university_names = []
    while True:
        rows = driver.find_elements(By.XPATH, '//tr[@data-v-ae1ab4a8=""]')
        for row in rows:
            university_name_elements = row.find_elements(By.XPATH, './/span[@class="univ-name"]')
            for element in university_name_elements:
                university_name = element.text.strip()
                university_names.append(university_name)  # Append the university name to the list

        try:
            next_page_button = driver.find_element(By.XPATH, '//li[@title="下一页"]')
            if next_page_button.get_attribute('aria-disabled') == 'true':
                print("Next Page button is not clickable. Stopping loop.")
                break
            next_page_button.click()
            wait()
        except NoSuchElementException as e:
            print("No more pages available.", e)
            break
    
    return university_names
back_to_first_page = driver.find_element(By.XPATH, '//li[@title="1"]')
back_to_first_page.click()
university = extract_names(driver)
print(university)


# In[21]:


def extract_cnci(driver):
    cnci_numbers = []
    while True:
        rows = driver.find_elements(By.XPATH, '//tr[@data-v-ae1ab4a8=""]')
        for row in rows:
            td_elements = row.find_elements(By.XPATH, './/td')
            if len(td_elements) >= 5:
                cnci_element = td_elements[4]  # Select the fifth td element (which is the cnci number)
                cnci_number = cnci_element.text.strip()
                cnci_numbers.append(cnci_number)  # Append the CNCI number to the list

        try:
            next_page_button = driver.find_element(By.XPATH, '//li[@title="下一页"]')
            if next_page_button.get_attribute('aria-disabled') == 'true':
                print("Next Page button is not clickable. Stopping loop.")
                break
            next_page_button.click()
            wait()
        except NoSuchElementException as e:
            print("No more pages available.", e)
            break

    return cnci_numbers
time.sleep(10)
back_to_first_page = driver.find_element(By.XPATH, '//li[@title="1"]')
time.sleep(10)
back_to_first_page.click()
time.sleep(12)
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(3)
click_cnci(driver)
time.sleep(10)
cnci = extract_cnci(driver)
print(cnci)


# In[22]:


def extract_top(driver):
    top_numbers = []
    while True:
        rows = driver.find_elements(By.XPATH, '//tr[@data-v-ae1ab4a8=""]')
        for row in rows:
            td_elements = row.find_elements(By.XPATH, './/td')
            if len(td_elements) >= 5:
                top_element = td_elements[4]  # Select the fifth td element
                top_number = top_element.text.strip()
                top_numbers.append(top_number)  # Append the top number to the list

        try:
            next_page_button = driver.find_element(By.XPATH, '//li[@title="下一页"]')
            if next_page_button.get_attribute('aria-disabled') == 'true':
                print("Next Page button is not clickable. Stopping loop.")
                break
            next_page_button.click()
            wait()
        except NoSuchElementException as e:
            print("No more pages available.", e)
            break

    return top_numbers
time.sleep(10)
back_to_first_page = driver.find_element(By.XPATH, '//li[@title="1"]')
time.sleep(10)
back_to_first_page.click()
time.sleep(12)
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(3)
click_top(driver)
time.sleep(10)
top = extract_top(driver)
print(top)


# In[23]:


# Append the data to the DataFrame
df["University"] = university
df["CNCI"] = cnci
df["TOP"] = top
df_shanghai = df

# Print the DataFrame
print(df_shanghai)
df_shanghai.to_excel('shanghai.xlsx', index=False)


# In[24]:


get_ipython().system('pip install fuzzywuzzy')
get_ipython().system('pip install python-Levenshtein')


# In[41]:


df_qs['University'] = df_qs['University'].str.strip()
df_the['University'] = df_the['University'].str.strip()
df_shanghai['University'] = df_shanghai['University'].str.strip()
# Convert university names to lowercase and remove special characters
df_qs['University'] = df_qs['University'].str.lower().replace('[^a-z0-9 ]', '', regex=True)
df_the['University'] = df_the['University'].str.lower().replace('[^a-z0-9 ]', '', regex=True)
# Convert university names to lowercase and remove special characters
df_shanghai['University'] = df_shanghai['University'].str.lower().replace('[^a-z0-9 ]', '', regex=True)


# In[42]:


from fuzzywuzzy import fuzz, process
import pandas as pd

# Define a function to find the best match for a given university name
def find_best_match(name, choices):
    best_match, score = process.extractOne(name, choices)
    if score >= 95:  # Adjust the threshold as needed
        return best_match
    else:
        return name

# Get unique university names from both dataframes
qs_universities = df_qs['University'].unique()
the_universities = df_the['University'].unique()

# Create a master list of all unique university names
all_universities = list(set(qs_universities))


# Standardize university names in df_the
df_the['New University'] = df_the.apply(lambda x: find_best_match(x['University'], all_universities), axis=1)

# Merge the dataframes based on standardized university names
merged_df = pd.merge(df_qs, df_the, on=['University', 'Country'], how='outer')

# Select the desired columns
merged_df = merged_df[['University', 'Country', 'QS Citations per Paper', 'QS Academic Reputation','QS Employer Reputation',
                       'Citations', 'Research', 'Teaching']]

# Display the merged dataframe
print(merged_df)


# In[43]:


from fuzzywuzzy import fuzz, process
import pandas as pd

# Assuming you have dataframes named df_qs and df_the

# Define a function to find the best match for a given university name
def find_best_match(name, choices):
    best_match, score = process.extractOne(name, choices)
    if score >= 95:  # Adjust the threshold as needed
        return best_match
    else:
        return name

# Get unique university names from both dataframes
shanghai_universities = df_shanghai['University'].unique()
merged_universities = merged_df['University'].unique()

# Create a master list of all unique university names
all_universities = list(set(merged_universities))

# Standardize university names in df_the
df_shanghai['new University'] = df_shanghai.apply(lambda x: find_best_match(x['University'], all_universities), axis=1)

# Merge the dataframes based on standardized university names
new_merged_df = pd.merge(merged_df, df_shanghai, on=['University'], how='outer')

# Select the desired columns
new_merged_df = new_merged_df[['University', 'Country', 'QS Citations per Paper', 'QS Academic Reputation','QS Employer Reputation',
                       'Citations', 'Research', 'Teaching', 'CNCI', 'TOP']]

# Display the merged dataframe
print(new_merged_df)


# In[44]:


from fuzzywuzzy import fuzz, process
import pandas as pd

# Assuming you have a dataframe named merged_df
# Define a function to find the best match for a given university name
def find_best_match(name, choices):
    best_match, score = process.extractOne(name, choices)
    if score >= 93:  # Adjust the threshold as needed
        return best_match
    else:
        return name

# Create a list of all unique university names
all_universities = new_merged_df['University'].unique()

# Standardize university names in the merged DataFrame
new_merged_df['University'] = new_merged_df.apply(lambda x: find_best_match(x['University'], all_universities), axis=1)

# Combine values for similar university names
for idx, row in new_merged_df.iterrows():
    university_name = row['University']
    
    # Find similar matches in the merged DataFrame based on university name (excluding the current row)
    similarity_threshold = 97  # Adjust the similarity score threshold as needed
    similar_matches = new_merged_df[new_merged_df.apply(lambda x: fuzz.token_sort_ratio(x['University'], university_name), axis=1) >= similarity_threshold]
    similar_matches = similar_matches[similar_matches.index != idx]
    
    # Check if there are any similar matches
    if not similar_matches.empty:
        # Get the first similar match (you can implement a more sophisticated logic here)
        similar_row = similar_matches.iloc[0]
        
        # Iterate through the columns to fill in missing values with non-null values from either row
        for column in new_merged_df.columns:
            if pd.isnull(row[column]) and not pd.isnull(similar_row[column]):
                new_merged_df.at[idx, column] = similar_row[column]
            elif pd.isnull(similar_row[column]) and not pd.isnull(row[column]):
                new_merged_df.at[idx, column] = row[column]

# Display the updated DataFrame
print(new_merged_df)


# In[45]:


# Fill NaN values with 0 for every row except 'country' column
country_column = new_merged_df['Country']
new_merged_df.drop('Country', axis=1, inplace=True)
new_merged_df.fillna(0, inplace=True)
new_merged_df['Country'] = country_column
new_merged_df[['University', 'Country', 'QS Citations per Paper', "Citations", 'CNCI', 'QS Academic Reputation',
              'QS Employer Reputation', 'Research', 'Teaching', 'TOP']]
new_merged_df


# In[51]:


import pandas as pd
new_merged_df['QS Citations per Paper'] = pd.to_numeric(new_merged_df['QS Citations per Paper'], errors='coerce')
new_merged_df['Citations'] = pd.to_numeric(new_merged_df['Citations'], errors='coerce')
new_merged_df['CNCI'] = pd.to_numeric(new_merged_df['CNCI'], errors='coerce')

# Calculate the "final citation score" for each row based on the specified logic
def calculate_final_score_citations(row):
    qs_citations_per_paper = row['QS Citations per Paper']
    citations = row['Citations']
    cnci = row['CNCI']

    if qs_citations_per_paper != 0 and citations != 0 and cnci != 0:
        final_score = (((qs_citations_per_paper + citations + cnci) / 3) / 100) * 0.8 + 0.2
    elif (qs_citations_per_paper != 0 and citations != 0) or (qs_citations_per_paper != 0 and cnci != 0) or (citations != 0 and cnci != 0):
        final_score = (((qs_citations_per_paper + citations + cnci) / 2) / 100) * 0.8 + 0.1
    elif qs_citations_per_paper != 0 or citations != 0 or cnci != 0:
        final_score = (max(qs_citations_per_paper, citations, cnci) / 100) * 0.8
    else:
        final_score = 0

    return (final_score*100)

# Apply the calculation to each row and create a new 'final citation score' column
new_merged_df['final citation score'] = new_merged_df.apply(calculate_final_score_citations, axis=1)

# Display the updated DataFrame
print(new_merged_df)


# In[53]:


def calculate_final_score_rep(row):
    cols = ['TOP', 'QS Academic Reputation', 'QS Employer Reputation', 'Research', 'Teaching']
    non_zero_cols = [col for col in cols if row[col] != 0]
    non_zero_count = len(non_zero_cols)

    # Convert relevant columns to numeric
    numeric_cols = row[non_zero_cols].apply(pd.to_numeric, errors='coerce')

    if non_zero_count == 5:
        final_score = (((numeric_cols.sum() / 5) / 100) * 0.8) + 0.2
    elif non_zero_count == 4:
        final_score = (((numeric_cols.sum() / 4) / 100) * 0.8) + 0.15
    elif non_zero_count == 3:
        final_score = (((numeric_cols.sum() / 3) / 100) * 0.8) + 0.1
    elif non_zero_count == 2:
        final_score = (((numeric_cols.sum() / 2) / 100) * 0.8) + 0.05
    elif non_zero_count == 1:
        final_score = (numeric_cols[non_zero_cols[0]] / 100) * 0.8
    else:
        final_score = 0

    return (final_score * 100)

# Apply the calculation to each row and create a new 'final reputation score' column
new_merged_df['final reputation score'] = new_merged_df.apply(calculate_final_score_rep, axis=1)

# Display the updated DataFrame
print(new_merged_df)


# In[54]:


new_merged_df['overall score'] = 0.2 * new_merged_df['final citation score'] + 0.8 * new_merged_df['final reputation score']
new_merged_df.sort_values(by='overall score', ascending=False, inplace=True)
new_merged_df.reset_index(drop=True, inplace=True)
new_merged_df.index += 1
new_merged_df.to_excel('FINAL_ranking_list.xlsx')

