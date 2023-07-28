import requests
import pandas as pd
import datetime as dt

# change here to change filename
filename = "recruitment.csv"
rec_file = requests.get("https://stats.mom.gov.sg/iMAS_Tables1/Time-Series-Table/mrsd_25_Qtly_and_annl_tsd_on_rec_by_ind_and_occ_grp.xlsx", allow_redirects=True)

# create dct as dictionary for mapping of column names
start_year = 2006; end_year = dt.datetime.now().year
year_range = end_year - start_year + 1

dct = {}

for i in range (year_range): #year index
    for j in range(1,5): #num quarters
        str = f"{j}Q" if i == 0 else f"{j}Q.{i}"
        dct[str] = f"{start_year} {j}Q"    
    start_year += 1

index_infocomm = 22; lst_index = [0, *range(index_infocomm, index_infocomm+3)]

df_rec = pd.read_excel(rec_file.content, sheet_name=3, header=3).drop(columns="OCCUPATIONAL GROUP").rename(columns=dct)

rec = df_rec.iloc[lst_index]

rec.to_csv(filename, index=False)
