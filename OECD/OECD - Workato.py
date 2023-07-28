# This dataset contains employment and the number of employees, broken down:
#   - by economic activities (1); by professional status (2)

# Motivation: OECD data shows us the international employment trends (change in values of employment over years), 
# which enables comparison of employment trends between Singapore and selected overseas countries (those that were picked out as tech hubs).

# This script is used to extract data by year for employment for the selected list of OECD Countries
# for the sector of Information and Communication (ISIC Rev 4). 

# If the list of countries needs to be changed, check for the country code to pull the data and 
# update C_API, inserting the correct value to get the correct column of data 

import requests
import json
import pandas as pd
import datetime as dt
import pycountry

# Location in returned dictionary, likely will not cause errors but may return wrong data, will need to check again
C_API = {'AUS': '0:15:1:0',
'ISR': '0:13:0:0',
'JPN': '0:13:2:0',
'KOR': '0:13:2:0',
'GBR': '0:10:2:0',
'EST': '0:11:2:0',
'FRA': '0:13:0:0',
'DEU': '0:13:2:0',
'IRL': '0:13:0:0',
'ITA': '0:13:2:0',
'NLD': '0:13:2:0',
'POL': '0:13:2:0',
'PRT': '0:13:2:0',
'ESP': '0:13:2:0',
'SWE': '0:13:2:0'}

# Country code used, it can be referenced from pycountry, but workato does not provide access to pycountry so this is used in the script on workato instead 
COUNTRY_CODE = {'AUS': 'Australia', 
          'ISR': 'Israel', 
          'JPN': 'Japan', 
          'KOR': 'Korea, Republic of', 
          'GBR': 'United Kingdom', 
          'EST': 'Estonia', 
          'FRA': 'France', 
          'DEU': 'Germany', 
          'IRL': 'Ireland', 
          'ITA': 'Italy', 
          'NLD': 'Netherlands', 
          'POL': 'Poland', 
          'PRT': 'Portugal', 
          'ESP': 'Spain', 
          'SWE': 'Sweden'}

# Used to ensure that the data is pulled until the current year - limitation is OECD may not provide all years until now
# Start year is from 2008 is because that is how far back the data is provided by OECD
start_year = 2008; end_year = dt.datetime.now().year
# Base link used for API call, with year updated till current year
base = f'''https://stats.oecd.org/SDMX-JSON/data/ALFS_EMP/COUNTRY_CODE.\
YAREV4+YA994TL1_ST+YA994AL1_ST+YA99A4L1_ST+YA994IL1_ST+YA99B4L1_ST+YA99C4L1_ST+YA99D4L1_ST+YA99E4L1_ST+YA99F4L1_ST+YA994SL1_ST+YA99G4L1_ST+YA99H4L1_ST+YA99I4L1_ST+YA99J4L1_ST+YA99K4L1_ST+YA99L4L1_ST+YA99M4L1_ST+YA99N4L1_ST+YA99O4L1_ST+YA99P4L1_ST+YA99Q4L1_ST+YA99X4L1_ST+YA99S4L1_ST+YA99T4L1_ST+YA99U4L1_ST.MA+FE+TT.A/\
all?startTime={start_year}&endTime={end_year}'''

# column_names is the structure for columns for the dataframe
column_names = ["Country Code", "Country"]
YEARS = [f'{year}' for year in range(start_year, end_year + 1)]
column_names.extend(YEARS)

df = pd.DataFrame(columns=column_names)
empty_item = "na" #used as the default value for empty cells of data, can also be np.nan

# base_row is an empty row with all empty values
base_row = {column_name:empty_item for column_name in column_names}

# Iterating through the countries
for c_code in C_API.keys():
    new_row = base_row.copy()
    # Update Country Code and Country for easier reference when viewing
    new_row["Country Code"] = c_code; 
    # pycountry.countries.get(alpha_3=C_API).name is the same as 
    # C_CODE[c_code] 
    new_row["Country"] = COUNTRY_CODE[c_code] #pycountry.countries.get(alpha_3=C_API).name

    # Replaces the country code from the base link to get API extraction for each country
    link = base.replace("COUNTRY_CODE", c_code)
    req = requests.get(link)

    # Getting the data from the API call
    JS = json.loads(req.text)
    test = JS['dataSets'][0]['series']
    data = test[C_API[c_code]]['observations']
    

    years_dct = JS['structure']['dimensions']['observation'][0]['values']
    years = [year['id'] for year in years_dct] # years where current data is present

    # Original data
    o_keys = [data[key][0] for key in data]
    # Assigning data to the new_row dictionary to insert into the dataframe
    for index in range(len(years)):
        real_year = years[index]
        o_index = o_keys[index]
        
        new_row[real_year] = o_index

    # Inserting new_row as a new row into the dataframe
    df.loc[len(df)] = new_row

# Writing the dataframe into a csv file
df.to_csv('OECD.csv', index=False, float_format='%.2f')
