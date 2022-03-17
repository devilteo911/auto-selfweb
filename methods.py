import os
import pathlib
import platform
import datetime
import requests
import pandas as pd
from datetime import date
from zipfile import ZipFile
from bs4 import BeautifulSoup
from typing import *
from selenium import webdriver
from win10toast import ToastNotifier
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException

CREDENTIALS_FILE = os.getcwd() + "/credentials.txt"
LINKS_FILE = os.getcwd() + "/links.csv"
URL_CHROMEDRIVER = (
    "https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip"
)


def credentials_handler(
    credential_file_path: str = CREDENTIALS_FILE,
) -> Tuple[str, str, str]:
    """
    It helps in the initial phase of credential creation if the `credential_file_path` is
    not present in path, otherwise it reads it and returns a triplet of credentials:
    username, password and chrome binaries path.

    Args:
        credential_file_path (str, optional): Path to the credential file.
        Defaults to CREDENTIAL_FILE.

    Returns:
        Tuple[str, str, str]: the username, password and chrome binaries path associated to
        a user.
    """
    credentials = ""
    if os.path.exists(credential_file_path):
        with open(credential_file_path, "r") as f:
            credentials = f.readlines()
        username = credentials[0].split()[0]
        password = credentials[1]
        browser_path = credentials[2]

    else:
        with open(credential_file_path, "w") as f:
            username = input("Type your INAZ username: ")
            password = input("Type your INAZ password: ")
            print(
                "\nTo find the executable you have to navigate the file explorer. The usual location is under either 'C:/Program Files/' or 'C:/Users/morom/AppData/Local/. In case of a custom location you have to figure it out by yourself :)\n"
            )
            browser_path = input("Place here your chrome.exe or brave.exe file: ")
            f.write(username + "\n")
            f.write(password + "\n")
            f.write(browser_path)
    return username, password, browser_path


def date_format(date: datetime, begin_month: bool = False) -> str:
    """
    Takes in input a datetime and a flag an returns a dd/mm/yyyy
    string date

    Args:
        date (datetime): date in datetime format
        begin_month (bool, optional): flag to choose the date range.
        If false it will pick today's date, otherwise the beginning of the month.
        Defaults to `False`.

    Returns:
        str: A dd/mm/yyyy string data
    """
    year = str(date.year)
    month = str(date.month)
    day = str(date.day)
    if not begin_month:
        return day + "/" + month + "/" + year
    else:
        return "01" + "/" + month + "/" + year


def chromedriver_updater(url: str) -> None:
    """
    It updates the chromedriver based on the latest update on Google
    website. If another version of chromedriver is present in the
    project folder it will be deleted and replace with the new one.

    Args:
        url (str): url to the google file location
    """
    # scraping the file from google's website
    req = requests.get("https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
    data = BeautifulSoup(req.text, "html.parser")
    filename_zip = "chromedriver.zip"
    curr_driver_path = os.getcwd() + "\\chromedriver.exe"
    url = url.format(data)
    r = requests.get(url)

    # retrieving data from the URL using get method
    with open(filename_zip, "wb") as f:
        # giving a name and saving it in any required format
        # opening the file in write mode
        f.write(r.content)

    # deleting the previous file version, if present
    if os.path.exists(curr_driver_path):
        file = pathlib.Path(curr_driver_path)
        file.unlink()

    # opening the zip file
    with ZipFile(filename_zip, "r") as zip:
        # list all the contents of the zip file
        zip.printdir()

        # extract all files
        print("extraction...")
        zip.extractall(path=os.getcwd())
        print("Done!")

    os.remove(filename_zip)


def binary_checker(path: str) -> webdriver.Chrome:
    """
    Based on the system you are on (either Windows or MacOS/Linux) it loads the
    browser driver (currently only chromium based browser are supported). If the
    driver it's outdated or missing it will updated using the `chromedriver_updater`
    function.

    Args:
        path (str): the location to the browser binary or executable

    Returns:
        webdriver.Chrome: the selenium Chrome webriver
    """
    global URL_CHROMEDRIVER
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    if platform.system() == "Windows":
        options.binary_location = path
        try:
            driver = webdriver.Chrome(
                options=options, executable_path=os.getcwd() + "/chromedriver.exe"
            )
        except (SessionNotCreatedException, WebDriverException) as e:
            chromedriver_updater(URL_CHROMEDRIVER)
            driver = webdriver.Chrome(
                options=options, executable_path=os.getcwd() + "/chromedriver.exe"
            )
    else:
        options.binary_location = (
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        )
        driver = webdriver.Chrome(
            options=options, executable_path=os.getcwd() + "/chromedriver"
        )

    return driver


def notify_me(start_work: str) -> None:
    """
    Notifies the user about it's daily shift at work based on when he/she
    badged.

    Args:
        start_work (str): The entrance time
    """
    toast = ToastNotifier()
    start_work = start_work.replace(" ", "")
    print(start_work)
    try:
        if datetime.datetime.now().weekday() != 4:  # it is not friday
            hh, mm = int(start_work.split(".")[0]) + 9, start_work.split(".")[1]
        else:
            hh, mm = int(start_work.split(".")[0]) + 7, start_work.split(".")[1]
    except ValueError:
        toast.show_toast(
            "SelfWeb",
            "The timetable may not be ready. Usually the infos are up at 11am, check it later!",
            duration=8,
            icon_path="INAZLogo.ico",
        )
    text = f"Oggi sei entrato alle {start_work} e uscirai alle {hh}:{mm}"
    if platform.system() == "Windows":
        toast.show_toast("SelfWeb", text, duration=8, icon_path="INAZLogo.ico")
    else:
        os.system(f"osascript -e 'display notification \"{text}\"'")


def links_extractor(file_path: str = LINKS_FILE) -> List[str]:
    """
    It reads a csv file and return a list of its content

    Args:
        file_path (str): path to file containing the links

    Returns:
        List[str]: the links of the file as a list
    """
    csv = pd.read_csv(file_path, sep=",")
    return csv["url"].values.tolist()
