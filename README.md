# Documentation - MPS + BG
This page details the work done by Sheline to extract, clean, and process the MPS and BG data sources.

## Windows Users
If you are using a Windows Machine, you need to use the Windows Subsystem for Linux (WSL). 
## Data Sources
### MPS
This is the IMDA Manpower Survey. It is administered by IMDA annually, and collates data points like employment and vacancy numbers, and a variety of other numbers.

Ideally, we want the 'Employment' and 'Vacancy' columns from the 'EmpVacDmd' sheet in the MPS Excel workbook to be fed into Tableau. To do that, we need to

1. Move the specific cells of the employment and vacancy numbers into a new sheet. Specifically, these cells should be located at cell A1, so that Tableau can digest the sheet correctly.
2. Map each job role to its SSOC ([Singapore Standard Occupational Classification](https://www.singstat.gov.sg/standards/standards-and-classifications/ssoc)). In MPS, there are only job roles listed without SSOCs, and we need to map the job roles to its SSOC for when we eventually put this data into Tableau and can only identify the numbers by the SSOC it's matched to.

### BG
This is Burning Glass. Specifically, we use the Labour Insight dashboard made by Burning Glass. On Labour Insight, we want to extract two main things.

1. Occupation Analysis
    - You can find this at Snapshots > Occupation Analysis.
    - We use this report to generate a list of skills needed for each SSOC<sup>1</sup> that we want to track.
2. Time Series Analysis
    - You can find this at Create Reports > Focus on - Time Series Analysis
    - We use this report to get the number of job postings on a monthly basis for each SSOC that we're tracking. These numbers give us a sense of the industry's demand for each occupation.

## Data Extraction + Preparation Pipeline
This section outlines the existing + planned pipeline to automatically extract and prepare the above 2 data sources for visualization in Tableau.

### MPS
1. Manual copy & paste of the 'EmpVacDmd' cells into the 'MPS Template' Excel workbook<sup>2</sup>. 
2. Excel will automatically map the job roles to SSOCs. This is done using a formula<sup>3</sup> that references a sheet that contains the job role to SSOC mapping.
3. (Planned) Excel<sup>4</sup> and do an "exploding" to deal with job roles that map to multiple SSOCs.
4. (Planned) Move the 'MPS Template' file into some previously decided upon location, for Tableau to ultimately read in.

### BG
1. A Workato recipe will be triggered on a schedule. This recipe will trigger an AWS Lambda function that will run a Selenium script that scrapes the BG data.
2. The BG data gets uploaded onto AWS S3.
3. Another Workato recipe gets triggered when the new file gets uploaded onto S3. It will be automatically sent as an attachment to your email<sup>5</sup>.

## Technical Details
### Deploying to AWS Lambda
If you require Selenium, you're gonna have to create a Docker container and deploy that to Lambda.

1. Install [node](https://nodejs.org/en/download)
    a. Type `which npm` to check the location of node. 
    b. Type `npm` to ensure that your WSL/Linux system is able to access node. 
    c. If there are any issues, update your WSL from 1 to 2 (or the latest version).
1. Navigate to [this](https://github.com/shleen/psd-lambda-functions) GitHub repository and clone the `template` folder.
2. Edit the `handler` function in `main.py` to include your code.
3. Edit `Dockerfile` after Line 15 to include `pip install` lines for all the packages your script requires.
4. Edit `serverless.yml`. Specifically, lines 2, 3, and 16.
4. (For first-time users) Set up `serverless`. To do  this, run `npm install -g serverless`. Then, configure serverless with your AWS credentials by running `serverless config credentials --provider aws --key <AWS_ACCESS_KEY> --secret <AWS_SECRET_KEY> -o`.
5. `cd` into the folder with your Lambda function
6. Run `sls deploy`
7. To invoke the function, run `sls invoke --function function_name`. The `function_name` here is what you set on line 16 from step 4 above.

## Footnotes
1&nbsp; We work with 5D SSOCs - 5-digit numerical codes that correspond to an occupation. For this report, Burning Glass only takes 4D SSOCs. This means that one 'dimension' of occupations are lost. i.e. SSOCs 12222 and 12223 refer to separate but similar occupations. The 4D SSOC 1222 will encapsulate both 12222 and 12223. This is a known limitation of Burning Glass and is something that has to be worked around.

2&nbsp; This step is necessary because the MPS is formatted to be easily human-readable, which also means that it isn't easily computer-readable. Additionally, from looking at previous years' MPSs, it appears that we can expect pretty significant changes in formatting. This means that any script to extract these cells automatically will very likely become non-workable by the next year.

3&nbsp; This is sliiightly complicated because we have one sheet that contains the SSOC to job role mapping. However, we've found that 

4&nbsp; We're using Excel to this because MPS is classified as Confidential (rather than Restricted) and trying to get clearance to upload MPS onto Workato, we think, will take a really long time + be almost impossible. Additionally, since the "exploding" step is not too too complicated, the plan now is to try to do all of this within Excel.

5&nbsp; This step currently sends the email to the recipient's junk mail, which is less than ideal. This happens because of the attachment -  emails sent with no attachment are placed into the inbox correctly. A possible alternative proposed by Luan Ting is to first zip the attachment up and then to password protect it. Apparently the TD team has used this solution for other use cases facing similar issues. Workato has provided a guide for doing this. 