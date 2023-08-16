import pdfplumber
import pandas as pd
import boto3
import os
from dotenv import load_dotenv
import time
import datetime

def handler(event=None, context=None):
    load_dotenv()
    s3_client = boto3.client('s3')

    # Initialise AWS client
    s3 = boto3.resource('s3',
        aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY'])

    # Download .pdf from S3 to /tmp/ in container
    file_to_download = 'test.pdf'
    download_to = r'/tmp/' + file_to_download
    s3_client.download_file('psd-dashboard-data', file_to_download, download_to)

    # TODO: Append all the saved .csv files to one master file
    # Extracting .pdf table as df
    pdf = pdfplumber.open(download_to)
    tables=pdf.pages[0].extract_tables()

    for i in range(len(tables)):
        x = pd.DataFrame(tables[i][1::],columns=tables[i][0])

        # Saving .csv on /tmp/
        save_as = r'/tmp/' + file_to_download[:-3] + str(i) + 'csv'
        x.to_csv(save_as)

        # Uploading .csv to S3
        timestamp = time.time()
        value = datetime.datetime.fromtimestamp(timestamp)
        human_time = value.strftime('%Y-%m-%d ') + str((int(value.strftime('%H'))+8)%24) + value.strftime('%M')
        s3_client.upload_file(save_as, 'psd-dashboard-data', file_to_download[:-4] + str(i) + f' {human_time}.csv')

handler()