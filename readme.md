# LinkedIn Profile Scraper

A Python-based LinkedIn profile scraper that uses Selenium and BeautifulSoup to extract profile information such as name, connections, skills, contact details, and more. The scraped data is stored in a CSV file and maintains a record of already-scraped profiles to avoid duplication in future runs.

## Features
Scrapes LinkedIn profiles listed in a CSV file, saving extracted data to a separate CSV.
Tracks scraped profiles by marking their status, so they are not scraped repeatedly.
Saves data in a consistent format, allowing for easy data analysis and reporting.
Automatically manages output folders and supports resuming from where it left off.
Validates each profile to determine if it’s potentially fake or a premium member.

## Prerequisites:
Python 3.6+
Google Chrome and ChromeDriver (ensure compatibility with your Chrome version)
LinkedIn account with a stored session in Chrome for authentication(Your linkedin account needs to be logged in before scraping)
LinkedIn URLs to scrape saved in a CSV file


## Required Python Libraries
Install these libraries if they are not already installed:
```bash
pip install -r requirements.txt
```

## Project Setup:
### Step 1: Configure Paths
Update these variables in the script with the correct paths for your setup:

```bash
CHROME_DRIVER_PATH = r'/path/to/chromedriver'
CHROME_BINARY_PATH = "/path/to/google-chrome"
PROFILE_URLS_FILE = '/path/to/profile_urls_file.csv'  # File containing LinkedIn profile URLs
output_dir = "Data"  # Directory to save scraped data
```

### Step 2: Setup Chrome Options
Update Chrome options in the script for proper access. Be sure to:

1. Create a new profile in your Chrome browser " eg. test " and then replace the profile name in the code.
2. Make sure to replace the login credentials in "config.ini" file in yours.

### Step 3: Prepare LinkedIn Profile URLs File
The profile URLs should be stored in a CSV file (profile_urls_file.csv) with each URL in a separate row. Add a Status column to track whether each profile has been scraped. If it doesn’t exist, the script will automatically add it.

## Directory Structure
The project structure should look like this
```bash
.
├── scrap.py           # The main scraping script
├── profile_urls_file.csv       # CSV file with LinkedIn URLs to scrape
├── config.ini                  # File for sensitive data like login Credentials.
├── requirements.txt            # File contaning the requirement names
└── Data                        # Folder to store the output CSV file
```

## Running the Scraper
1. *Execute the Script:* Run the Python script from the command line:

```bash

python scrap.py

```

2. *Monitoring Progress:* The script will log progress as it runs, reporting any errors encountered during scraping.

3. *Data Storage:* Scraped data is stored in Data/scraped_data.csv. If the file already exists, new data will be appended without overwriting.

## CSV Columns in Output File
The output CSV file will contain the following columns:

### *Name:* Name of the profile owner.
### *Profile Validation:* Indicates whether the profile might be fake.
### *Connections:* Number of LinkedIn connections.
### *Current Company:* Profile’s current listed company.
### *Image URL:* URL of the profile image.
### *Skills:* List of skills associated with the profile.
### *Title:* Current title.
### *Email and Phone:* Contact information.
### *Verified:* Whether the profile is verified.
### *Premium:* Indicates premium membership status.
### *Projects and Experience:* Lists of projects and job experiences.

# Code Explanation

## Profile Validation
### The script labels profiles as "Potentially Fake Profile" if:
Connection count is below 50.
The profile lacks job experience, skills, or a project.
No profile image or premium membership is found.

## Additional Functions
*Profile Validation:* Checks the profile’s connections, skills, and job history.
*Skills and Projects Extraction:* Accesses different sections of the profile to gather additional details.
*Email and Phone Extraction:* Extracts contact information, if available.

## Error Handling and Limitations
*Errors:* Any errors during scraping are printed to the console.
*Rate Limiting:* LinkedIn may temporarily block scraping activities if it detects too many requests. Use appropriate delays to avoid account restrictions.
*File Updates:* The profile_urls_file.csv is updated after each run, setting the status of successfully scraped profiles to scraped.

## Disclaimer
*Note:* Scraping LinkedIn is against their Terms of Service, and this project is for educational purposes only. Be aware of the legal implications and potential account restrictions if you choose to run this script.

