# Requires ChromeDriver.exe in local path, or profide an import.
# Had to do it this way because of org self signed cert issues I couldn't be bothered circumventing. 
siteUrl = "http://<project-url>/<site-url>/_layouts/15/pwa/Admin/ManageUsers.aspx"
headless = True
import subprocess
import sys
import os

subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
import time

try:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # Setup for ChromeDriver
    webdriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('log-level=3')
    service = ChromeService(executable_path=webdriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    with open('users.txt', 'a') as f:
        f.write("Processed users:" + '\n')
        f.close()
    def update_claim(page: int):
        # Load the webpage
        driver.get(siteUrl)

        # Wait for the table to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers')))

        # Navigate pages if necessary
        if page > 0:
            for x in range(0, page):
                nextButton = driver.find_element(By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers_ctl204_ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers_NextGridPage')
                nextButton.click()
                wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers')))

        # Find the table
        table = driver.find_element(By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers')

        # Get all rows in the table except headers
        rows = table.find_elements(By.XPATH, ".//tr[not(contains(@class, 'XmlGridTitleRow'))]")

        rowCount = len(rows) - 1

        for x in range(0, rowCount):
            # Find the table
            table = driver.find_element(By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers')
            
            # Get all rows in the table except headers
            wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers')))
            rows = table.find_elements(By.XPATH, ".//tr[not(contains(@class, 'XmlGridTitleRow'))]")
            row = rows[x]
            links = row.find_elements(By.XPATH, ".//td[2]//a")
            name = row.find_element(By.XPATH, ".//td[2]").text
            claim = row.find_element(By.XPATH, ".//td[4]").text
            status = row.find_element(By.XPATH, ".//td[5]").text
            print("\nProcessing " + name + ".\n Row " + str(x + 1) + " of " + str(rowCount) + " on Page: " + str(page + 1) + "\n")
            
            with open('users.txt', 'r') as f:
                if name in f.read():
                    print('User already processed. Skipping...\n')
                    f.close()
                    continue

            with open('users.txt', 'a') as f:
                f.write(name + '\n')
                f.close()

            if links and claim.startswith('GCCC') and status == 'Active':
                # Click the link directly
                print('Updating claim for ' + name)
                links[0].click()
            else:
                continue

            # Wait for the new page to load
            wait.until(EC.presence_of_element_located((By.ID, 'idBtnCancel')))
            # Check for the presence of the alert
            alert_elements = driver.find_elements(By.XPATH, '//span[@role="alert"]')
            if alert_elements:
                alert = alert_elements[0]
                print('Alert: ' + alert.text)
                with open('usersRequiringAction.txt', 'a') as f:
                    f.write('Possible action required for ' + name + '. Profile states: ' + alert.text + '\n')
                    f.close()

            # Check for the presence of the 'Save' button
            save_button_elements = driver.find_elements(By.ID, 'idBtnSubmit')
            save_button = save_button_elements[0]
            if save_button.get_attribute('disabled'):
                save_button_enabled = False
            else:
                save_button_enabled = True

            # If the 'Save' button is not present, or if the alert is present, click 'Cancel'
            if not save_button_enabled or alert_elements:
                cancel_button_elements = driver.find_elements(By.ID, 'idBtnCancel')
                if cancel_button_elements:
                    cancel_button = cancel_button_elements[0]
                    cancel_button.click()
            else:
                # If the 'Save' button is present and the alert is not present, click 'Save'
                save_button.click()
            wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers')))
            # Navigate pages if necessary
            if page > 0:
                for x in range(0, page):
                    nextButton = driver.find_element(By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers_ctl204_ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers_NextGridPage')
                    nextButton.click()
                    wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers')))

        wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers')))
        try: 
            next = driver.find_element(By.ID, 'ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers_ctl204_ctl00_ctl00_PlaceHolderMain_PWA_PlaceHolderMain_idGrdUsers_NextGridPage')
            update_claim(page + 1)
        except:
            print('Done')
            driver.quit()
            

    update_claim(0)


except Exception as e:
    print(f"An error occurred: {e}")
