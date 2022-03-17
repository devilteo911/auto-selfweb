# Imports
import os
import time
import datetime
from typing import *
from methods import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():

    # loading secrets :)
    logon_page, unk_url_1, unk_url_2 = links_extractor()
    USERNAME, PASSWORD, BROWSER_PATH = credentials_handler()

    # loading the driver
    driver = binary_checker(BROWSER_PATH)
    driver.get(logon_page)

    # finding page elements
    dominio = driver.find_element(by=By.NAME, value="Dominio")
    user = driver.find_element(by=By.NAME, value="Utente")
    pw = driver.find_element(by=By.NAME, value="Pwd")
    logon = driver.find_element(by=By.NAME, value="SUBMIT1")

    dominio.send_keys("RILPRES")
    user.send_keys(USERNAME)
    pw.send_keys(PASSWORD)

    # the submit button something goes crazy but it works :)
    try:
        logon.click()
    except Exception:
        pass

    time.sleep(1)

    start_date = date_format(datetime.datetime.now())
    end_date = date_format(datetime.datetime.now())

    # go to the first hidden page
    driver.get(unk_url_1.format(start_date, end_date))

    # go to the second hidden page
    driver.get(unk_url_2.format(USERNAME[-4:]))

    # wait until I find a certain element in the page
    wait = WebDriverWait(driver, 100)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "textcontent")))

    start_work = driver.find_element(
        by=By.XPATH, value='//*[@id="TblDiv"]/tbody/tr/td/table/tbody/tr[2]/td[3]/font'
    ).text
    notify_me(start_work)


if __name__ == "__main__":
    main()
