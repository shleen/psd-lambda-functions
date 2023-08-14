# TODO: change the file paths to /tmp
import pdfplumber
import pandas as pd
import boto3
import os
from dotenv import load_dotenv

load_dotenv()
s3_client = boto3.client('s3')

s3 = boto3.resource('s3',
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY'])

# TODO: change to s3 path
download_to = r'C:/Users/fuwen/Downloads/NTU GES 2022.pdf'
file_to_download = 'NTU GES 2022.pdf'

s3_client.download_file('psd-dashboard-data', file_to_download, download_to)

# TODO: change to s3 path, download to /tmp and then do the extraction there
save_as = r'C:/Users/fuwen/Downloads/NTU GES 2022.csv'

pdf = pdfplumber.open(download_to)
table=pdf.pages[0].extract_table()
x = pd.DataFrame(table[1::],columns=table[0])
x.to_csv(save_as)