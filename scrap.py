import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import re
import random
import sys
import configparser
import shutil

# Paths
CHROME_DRIVER_PATH = shutil.which("chromedriver") 
CHROME_BINARY_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_URLS_FILE = 'profile_urls_file.csv' 
output_dir = "Data"

# Configuration
config = configparser.ConfigParser()
config.read("config.ini")  # Replace with your config file path
username = "akashpauchary77@gmail.com"
password = config.get("linkedin", "password")

# Create "Data" directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def get_user_data_dir():
    # Determine the user data directory based on the OS
    if sys.platform.startswith('linux'):
        return os.path.expanduser("~/.config/google-chrome/")  # For Linux
    elif sys.platform == "win32":
        return os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data')  # For Windows
    elif sys.platform == "darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/Google/Chrome/")  # For macOS
    else:
        raise Exception("Unsupported platform")

# Get the user data directory
user_data_dir = get_user_data_dir()
profile_directory = "Default"

# Chrome options
options = webdriver.ChromeOptions()
options.binary_location = CHROME_BINARY_PATH
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--enable-logging")
options.add_argument("--v=1")
options.add_argument(f"user-data-dir={user_data_dir}tarun")
options.add_argument(f"profile-directory={profile_directory}")

# Function to validate LinkedIn URL format
def validate_profile_url(url):
    return re.match(r'https://www\.linkedin\.com/in/.*', url)

# Initialize profile_data to avoid NameError
profile_data = []

# Load the CSV and filter out previously scraped URLs
df = pd.read_csv(PROFILE_URLS_FILE)

# Ensure "Status" column exists; if not, add it
if 'Status' not in df.columns:
    df['Status'] = 'pending'  # Default status for all URLs

def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

# Filter URLs that are pending to scrape
urls_to_scrape = [url.strip() for url in df[df['Status'] != 'scraped'].iloc[:, 0] if validate_profile_url(url)]

# Start scraping
try:
    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)
    driver.get("https://www.linkedin.com/feed/")
    
    time.sleep(random.uniform(0.1, 0.2))

    if 'login' in driver.current_url:
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "username")))
        username_field = driver.find_element(By.ID, "username")
        human_typing(username_field, username)
        password_field = driver.find_element(By.ID, "password")
        human_typing(password_field, password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

    WebDriverWait(driver, 50).until(EC.url_contains("feed"))

    for url in urls_to_scrape:
        driver.get(url.strip())  # Clean URL
        time.sleep(5)  # Wait for the page to load

        try:
            # Scraping logic
            src = driver.page_source
            soup = BeautifulSoup(src, 'html.parser')

            # Profile data extraction
            name = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Name not found"
            connections_elem = soup.find('li', class_='text-body-small')
            connections = connections_elem.find('span', class_='t-bold').get_text(strip=True) if connections_elem else "Connections not found"

            try:
                connections_int = int(re.sub(r'\D', '', connections))  
            except ValueError:
                connections_int = 0

            current_company = soup.find('button', attrs={'aria-label': lambda x: x and "Current company:" in x})
            company_name = current_company['aria-label'].split("Current company: ")[1].split(". Click")[0] if current_company and current_company.has_attr('aria-label') else "Company not found"

            img_tag = soup.find('img')
            img_src = img_tag['src'] if img_tag and img_tag.has_attr('src') else "Image source not found"

            # Navigate to Skills page
            skills = []
            driver.get(f"{url.strip()}details/skills/")
            time.sleep(3)
            skills_page = BeautifulSoup(driver.page_source, 'html.parser')
            main_div = skills_page.find('section', class_="artdeco-card pb3")

            if main_div:
                skills_section = main_div.find_all('div', class_="display-flex align-items-center mr1 hoverable-link-text t-bold")
                for skill_div in skills_section:
                    skill_text = skill_div.find('span', {'aria-hidden': 'true'}).get_text(strip=True)
                    skills.append(skill_text)

            # Navigate to Contact Info page
            email, phone = "Email not found", "Phone not found"
            driver.get(f"{url.strip()}overlay/contact-info/")
            time.sleep(3)
            contact_page = BeautifulSoup(driver.page_source, 'html.parser')
            email_elem = contact_page.find('a', href=re.compile(r'mailto:'))
            phone_elem = contact_page.find('a', href=re.compile(r'tel:'))
            if email_elem:
                email = email_elem.get_text(strip=True)
            if phone_elem:
                phone = phone_elem.get_text(strip=True)

            # Navigate to Verification page
            verified = "No"
            driver.get(f"{url.strip()}overlay/about-this-profile/")
            time.sleep(3)
            verification_page = BeautifulSoup(driver.page_source, 'html.parser')
            if verification_page.find('span', class_='pv-profile-section__verified-badge'):
                verified = "Yes"

            # Extracting Title
            title_elem = soup.find('div', class_='text-body-medium')
            title = title_elem.get_text(strip=True) if title_elem else "Title not found"

            # Check for premium membership
            premium = "No"
            if soup.find('span', class_='pv-member-badge pv-member-badge--for-top-card'):
                premium = "Yes"

            # Extracting Projects
            driver.get(f"{url.strip()}details/projects/")
            time.sleep(3)
            project_page = BeautifulSoup(driver.page_source, 'html.parser')
            main_div = project_page.find('section', class_="artdeco-card pb3")
            projects = []
            if main_div:
                projects_section = main_div.find_all('div', class_="display-flex align-items-center mr1 t-bold")
                for project_div in projects_section:
                    project_text = project_div.find('span', {'aria-hidden': 'true'}).get_text(strip=True)
                    projects.append(project_text)

            # Extracting Job Experience
            driver.get(f"{url.strip()}details/experience/")
            time.sleep(3)
            experience_page = BeautifulSoup(driver.page_source, 'html.parser')
            main_div = experience_page.find('section', class_="artdeco-card pb3")
            job_experience = []
            if main_div:
                experience_section = main_div.find_all('div', class_="display-flex align-items-center mr1 t-bold")
                for experience_div in experience_section:
                    experience_text = experience_div.find('span', {'aria-hidden': 'true'}).get_text(strip=True)
                    job_experience.append(experience_text)

            # Profile validation
            isFake = 'Valid Profile'
            if connections_int < 50 or len(job_experience) < 1 or img_src == "Image source not found" or len(skills) < 1 or len(projects) < 1 or premium == 'No':
                isFake = 'Potentially Fake Profile'

            profile_data.append({
                "Name": name,
                "Profile Validation": isFake,
                "Connections": connections,
                "Current Company": company_name,
                "Image URL": img_src,
                "Skills": skills,
                "Title": title,
                "Email": email,
                "Phone": phone,
                "Verified": verified,
                "Premium": premium,
                "Projects": projects,
                "Experience": job_experience
            })

            # Mark this URL as "scraped" in the DataFrame
            df.loc[df.iloc[:, 0] == url, 'Status'] = 'scraped'

        except Exception as e:
            print(f"Error while scraping profile at {url}: {e}")

finally:
    # Quit driver if it exists
    driver.quit()
    df.to_csv(PROFILE_URLS_FILE, index=False)
    df_profiles = pd.DataFrame(profile_data)
    csv_file_path = os.path.join(output_dir, "scraped_data.csv")
    if os.path.exists(csv_file_path):
        df_profiles.to_csv(csv_file_path, mode='a', header=False, index=False)  
    else:
        df_profiles.to_csv(csv_file_path, mode='w', header=True, index=False)  
    print("Scraping completed. Data saved to:", csv_file_path)
