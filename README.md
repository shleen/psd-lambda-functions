# Documentation  
This page details the work done by IMDA PSD Interns (Sheline, Benedict, Aarthi, Anir, Vania and Fu Wen) to extract, clean, and process data sources for a J&S dashboard.

## Policy Questions
1. Comparing the supply of tech talent and demand for tech jobs in Singapore
    - What is the supply for a certain SSOC?
    - What is the demand for a certain SSOC?
    - Is there a mismatch between supply and demand?
2. Comparing the difference in supply and demand between Singapore and other countries
3. Considering what can be done to tackle the gaps in 1. and 2. 

## Non-Classified Data Sources
### \[Supply] University Rankings (QS + THE + SH)
We extract the following data points from 3 ranking system websites:
#### Quacquarelli Symonds (QS) Rankings for Computer Science and Information Systems.
1. University
2. Country
3. Citations Per Paper Score
4. Academic Reputation Score
5. Employer Reputation Score

#### Times Higher Education Rankings for Computer Science
1. University
2. Country
3. Citations Per Paper Score
4. Research Score
5. Teaching Score

#### Shanghai Rankings for Computer Science and Engineering
1. University
2. Category Normalized Citation Impact (CNCI) Score -- ratio of citations of papers published to the average citations of papers
3. Top Journals (TOP) Score --number of papers published in top journals in an academic subject

#### Combining
In the "uni_rankings" folder, we store the "uni_rankings_full_script.ipnyb" notebook which scrapes uni ranking information from QS, THE, SH websites. It combines them into 1 final ranking csv file "FINAL_ranking_list.csv" by combining/weighting scores from all 3 ranking systems.

The "qs_csv", "sh_csv", "the_csv" csv files contain the 2023 ranking information used in the "merging.ipnyb" notebook. This notebook shows just the combining code given existing data.

The Overall Score comprises 80% Overall (across all 3 rankings) Repuatation Score and 20% Citation Score. We also normalized for missing data points.

### \[Supply] MOM Recruitment and Resignation Rate
This data is taken directly from the Ministry of Manpower (MOM) website 
([link](https://stats.mom.gov.sg/pages/labourturnovertimeseries.aspx)). 
The current "API" call for this script goes into the link and accesses the public URL for the file and may not work in the future. 
However, the link earlier is of the original public page, and any updates should be able to be accessed from there. 
It comprises of data for the Infocomm industries (2D SSICs of 58-63). The motivation behind this data is:

1. **Recruitment Rate**: The recruitment rate is useful as another data source to compare for output of tech talent.
2. **Resignation rate**: The resignation rate is useful to compare and see if there is a higher than normal resignation rate for the Infocomm sector. 

### [Supply & Demand] US BLS
United States Bureau of Labour Statistics (US BLS) is the principal fact-finding agency for the U.S. government in the broad field of labor economics and statistics.

This can be used to find
1.	Demand/Vacancies for Tech Occupations with respect to US
2.	Which sectors in the US have the highest employment of tech occupations

We extract:
1. Occupation
2. Employment Numbers (in 1000s)
3. Wages

### \[Demand] BG
Burning Glass Singapore (BG). We use the Labour Insight dashboard made by BG. We generate 2 separate reports:

1. Occupation Analysis
    - You can find this at Snapshots > Occupation Analysis.
    - We use this report to generate a list of skills needed for each SSOC<sup>1</sup> that we want to track.
2. Time Series Analysis
    - You can find this at Create Reports > Focus on - Time Series Analysis
    - We use this report to get the number of job postings on a monthly basis for each SSOC that we're tracking. These numbers give us a sense of the industry's demand for each occupation.

### \[Supply] CB Insights
CB Insights provides market intelligence on high growth private companies and investor activities.

We extract:
1. Search Input (To check if we are searching for the correct items)
2. Company Name
3. URL (To check if it is the correct company, should we find any inconsistencies with other rows)
4. Total Funding (Funding/Investment amount)
5. Description (To check if it is the correct company based on what they do)
6. Total Headcount (Potential datapoint to see where the tech talent is going and if there are any emerging companies/industries)
7. Country
8. Sector
9. Industry
10. Sub-Industry
11. Latest Valuation

CB Insights groups campanies under Sector -> Industry -> Sub-Industry. We currently pull data from 6 Sectors:
1. Computer Hardware & Services
2. Electronics
3. Media (Traditional)
4. Internet
5. Mobile & Telecommunications
6. Software (non-internet/mobile)

### \[Demand] OECD
Organisation for Economic Co-operation and Development (OECD). 

This can be used to:
1. Identify trends in employment numbers across various countries
2. Compare global trends with Singapore's

We extract: 
1. Employment numbers of the Information and Commuication sectors/industries per year (2008-present)

## Data Extraction + Preparation Pipeline
This section outlines the existing + planned pipeline to automatically extract and prepare the above data sources for visualization in Tableau.

### QS, THE, SHANGHAI
1. A Workato recipe will be triggered on a schedule via a Workato recipe function call. 
This recipe will trigger an AWS Lambda function that will run a Selenium script that scrapes the QS, THE and Shanghai Rankings data, 
as well as, combines the three scripts and calculates an overall combined score data.
2. The overall combined score data gets uploaded onto AWS S3.
3. Another Workato recipe gets triggered when the new file gets uploaded onto S3. It will be automatically sent as an attachment to your email<sup>5</sup>. 

### MPS
1. Manual copy & paste of the 'EmpVacDmd' cells into the 'MPS Template' Excel workbook<sup>2</sup>. 
2. Excel will automatically map the job roles to SSOCs. This is done using a formula<sup>3</sup> that references a sheet that contains the job role to SSOC mapping.
3. (Planned) Excel<sup>4</sup> and do an "exploding" to deal with job roles that map to multiple SSOCs.
4. (Planned) Move the 'MPS Template' file into some previously decided upon location, for Tableau to ultimately read in.

### US BLS
1. A Workato recipe will be triggered on a schedule via a Workato recipe function call. 
This recipe will trigger an AWS Lambda function that will run a Selenium script that pulls the US BLS data.
2. The US BLS data gets uploaded onto AWS S3.
3. Another Workato recipe gets triggered when the new file gets uploaded onto S3. It will be automatically sent as an attachment to your email<sup>5</sup>.

### BG
1. A Workato recipe will be triggered on a schedule via a Workato recipe function call. 
This recipe will trigger an AWS Lambda function that will run a Selenium script that pulls the BG data.
2. The BG data gets uploaded onto AWS S3.
3. Another Workato recipe gets triggered when the new file gets uploaded onto S3. It will be automatically sent as an attachment to your email<sup>5</sup>.

### OECD
1. A Workato recipe will be triggered on a schedule. This recipe will trigger a Python API call that will extract the OECD data.
2. The OECD data will be cleaned.
3. The final csv file with the clean data will be sent as an attachment via email.

### CB Insights
1. A Workato recipe will be triggered on a schedule via a Workato recipe function call. 
This recipe will trigger an AWS Lambda function that will run a Selenium script that scrapes the company data from CB Insights.
2. The CB Insights data gets uploaded onto AWS S3.
3. Another Workato recipe gets triggered when the new file gets uploaded onto S3. It will be automatically sent as an attachment to your email<sup>5</sup>.

### MOM Recruitment and Resignation Rate
Process for both Recruitment and Resignation Rate is the same: 

1. A Workato recipe will be triggered on a schedule. This recipe will trigger a Python "API" call from a public URL that will extract the MOM data.
2. The MOM data will be cleaned and the relevant rows will be stored in a file. 
3. The final csv file with the clean data will be sent as an attachment via email.

### MPS (KIV)
IMDA Manpower Survey (MPS). It is administered by IMDA annually and collates data points like employment and vacancy numbers, and a variety of other numbers.
 
We want the 'Employment' and 'Vacancy' columns from the 'EmpVacDmd' sheet in the MPS Excel workbook to be fed into Tableau. To do that, we need to

1. Move the specific cells of the employment and vacancy numbers into a new sheet. Specifically, these cells should be located at cell A1, so that Tableau can digest the sheet correctly.
2. Map each job role to its SSOC ([Singapore Standard Occupational Classification](https://www.singstat.gov.sg/standards/standards-and-classifications/ssoc)). In MPS, there are only job roles listed without SSOCs, and we need to map the job roles to its SSOC for when we eventually put this data into Tableau and can only identify the numbers by the SSOC it's matched to.

## Technical Details
### Note for Windows Users
If you are using a Windows Machine, you need to use the Windows Subsystem for Linux (WSL). 
### Deploying to AWS Lambda
If you require Selenium, you're gonna have to create a Docker container and deploy that to Lambda.

1. Install [node](https://nodejs.org/en/download)
    a. Type `which npm` to check the location of node. 
    b. Type `npm` to ensure that your WSL/Linux system is able to access node. 
    c. If there are any issues, update your WSL from 1 to 2 (or the latest version).
2. Navigate to [this](https://github.com/shleen/psd-lambda-functions) GitHub repository and clone the `template` folder.
3. Edit the `handler` function in `main.py` to include your code.
4. Edit `Dockerfile` after Line 15 to include `pip install` lines for all the packages your script requires.
5. Edit `serverless.yml`. Specifically, lines 2, 3, and 16.
6. (For first-time users) Set up `serverless`. To do  this, run `npm install -g serverless`. Then, configure serverless with your AWS credentials by running `serverless config credentials --provider aws --key <AWS_ACCESS_KEY> --secret <AWS_SECRET_KEY> -o`.
7. `cd` into the folder with your Lambda function
8. Run `sls deploy --function function_name`
9. To invoke the function, run `sls invoke --function function_name`. The `function_name` here is what you set on line 16 from step 4 above.

## Footnotes
1&nbsp; We work with 5D SSOCs - 5-digit numerical codes that correspond to an occupation. For this report, Burning Glass only takes 4D SSOCs. This means that one 'dimension' of occupations are lost. i.e. SSOCs 12222 and 12223 refer to separate but similar occupations. The 4D SSOC 1222 will encapsulate both 12222 and 12223. This is a known limitation of Burning Glass and is something that has to be worked around.

2&nbsp; This step is necessary because the MPS is formatted to be easily human-readable, which also means that it isn't easily computer-readable. Additionally, from looking at previous years' MPSs, it appears that we can expect pretty significant changes in formatting. This means that any script to extract these cells automatically will very likely become non-workable by the next year.

3&nbsp; This is sliiightly complicated because we have one sheet that contains the SSOC to job role mapping. However, we've found that 

4&nbsp; We're using Excel to this because MPS is classified as Confidential (rather than Restricted) and trying to get clearance to upload MPS onto Workato, we think, will take a really long time + be almost impossible. Additionally, since the "exploding" step is not too too complicated, the plan now is to try to do all of this within Excel.

5&nbsp; This step currently sends the email to the recipient's junk mail, which is less than ideal. This happens because of the attachment -  emails sent with no attachment are placed into the inbox correctly. A possible alternative proposed by Luan Ting is to first zip the attachment up and then to password protect it. Apparently the TD team has used this solution for other use cases facing similar issues. Workato has provided a guide for doing this. 
