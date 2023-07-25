import requests
import json
import pandas as pd
import datetime as dt
import pycountry
import pprint
import time

# TIME_START = time.time()

pp = pprint.PrettyPrinter()

# Location in returned dictionary, likely will not cause errors but may return wrong data, will need to fact check again
C_CODE = {'AUS': '0:15:1:0',
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

start_year = 2008; end_year = dt.datetime.now().year

base = f'''https://stats.oecd.org/SDMX-JSON/data/ALFS_EMP/COUNTRY_CODE.\
YAREV4+YA994TL1_ST+YA994AL1_ST+YA99A4L1_ST+YA994IL1_ST+YA99B4L1_ST+YA99C4L1_ST+YA99D4L1_ST+YA99E4L1_ST+YA99F4L1_ST+YA994SL1_ST+YA99G4L1_ST+YA99H4L1_ST+YA99I4L1_ST+YA99J4L1_ST+YA99K4L1_ST+YA99L4L1_ST+YA99M4L1_ST+YA99N4L1_ST+YA99O4L1_ST+YA99P4L1_ST+YA99Q4L1_ST+YA99X4L1_ST+YA99S4L1_ST+YA99T4L1_ST+YA99U4L1_ST.MA+FE+TT.A/\
all?startTime={start_year}&endTime={end_year}'''

column_names = ["Country Code", "Country"]
YEARS = [f'{year}' for year in range(start_year, end_year + 1)]
column_names.extend(YEARS)

df = pd.DataFrame(columns=column_names)

base_row = {column_name:"na" for column_name in column_names}

for c_code in C_CODE.keys():
    new_row = base_row.copy()
    new_row["Country Code"] = c_code; new_row["Country"] = pycountry.countries.get(alpha_3=c_code).name

    link = base.replace("COUNTRY_CODE", c_code)
    req = requests.get(link)

    JS = json.loads(req.text)

    test = JS['dataSets'][0]['series']
    data = test[C_CODE[c_code]]['observations']
    
    years_dct = JS['structure']['dimensions']['observation'][0]['values']
    years = [year['id'] for year in years_dct]

    o_keys = [data[key][0] for key in data]
    for index in range(len(years)):
        real_year = years[index]
        o_index = o_keys[index]
        
        new_row[real_year] = o_index

    df.loc[len(df)] = new_row

df.to_csv('OECD.csv', index=False, float_format='%.2f')
