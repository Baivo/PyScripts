# Checks the Steam Workshop for the titles of mods in the Sandbox_config.sbc file
# Replace the file name with the name of your Sandbox_config.sbc file, or any other SBC/XML containing SE formatted workshop mod items
# Output is a text file with the status of each mod item, and the title if found

import subprocess
import sys

subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def construct_urls_from_sbc(file_name):
    with open(file_name, 'r') as file:
        data = file.read()

    soup = BeautifulSoup(data, 'xml')

    mod_items = soup.find_all('ModItem')

    base_url = "https://steamcommunity.com/sharedfiles/filedetails/?id="

    # setup for headless chrome
    webdriver_path = ChromeDriverManager().install()
    options = Options()
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(executable_path=webdriver_path, options=options)

    for item in mod_items:
        pub_id = item.find('PublishedFileId').text
        url = base_url + pub_id

        driver.get(url)
        time.sleep(2)  # Wait a bit for the page to load

        try:
            title_div = driver.find_element(By.CLASS_NAME, 'workshopItemTitle')
            status = "FOUND - Title: "
            title = title_div.text

        except Exception as e:
            status = "NOT FOUND - UNAVAILABLE OR REMOVED"
            title = ""

        with open('workshop_titles.txt', 'a') as f:
            f.write(f'{url} - {status}{title}\n')

    driver.quit()

construct_urls_from_sbc('Sandbox_config.sbc')
