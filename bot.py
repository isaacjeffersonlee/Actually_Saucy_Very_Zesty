import yaml
import time
import datetime
import platform
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchWindowException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from rich.console import Console  # Pretty printing

console = Console()


def instantiate_driver() -> WebDriver:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if platform.system() == "Windows":
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    elif platform.system() == "Darwin":  # MacOS
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    else:  # Linux
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--no-sandbox")
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--allow-running-insecure-content")
    return webdriver.Chrome(options=options)


def waited_find_element(driver, by: By, value: str, timeout: int = 6) -> WebElement:
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def login(driver: WebDriver, asvz_id: str, asvz_password: str) -> None:
    try:
        waited_find_element(driver=driver, by=By.ID, value="AsvzId").send_keys(asvz_id)
        waited_find_element(driver=driver, by=By.ID, value="Password").send_keys(
            asvz_password
        )
        waited_find_element(
            driver=driver,
            by=By.XPATH,
            value='//*[@id="collapse_asvz"]/div/form/div[3]/button',
        ).click()
        console.log("Success: Logged in!")
    except (TimeoutException, StaleElementReferenceException) as e:
        console.log("Error: Logging in!")
        pass


def click_login_button(driver: WebDriver) -> None:
    console.log("Looking for login button...")
    try:
        # Get the button to go to the login page
        waited_find_element(
            driver=driver,
            by=By.XPATH,
            value="/html/body/app-root/div/div[2]/app-lesson-details/"
            + "div/div/app-lessons-enrollment-button/button",
        ).click()
        console.log("Login button clicked!")
    except TimeoutException:
        console.log("Unable to find the login button before timeout!")


def click_enroll_button(driver: WebDriver) -> None:
    console.log("Clicking enroll button...")
    # ASVZ Likes to change these, probably to throw people like us off.
    possible_xpaths = (
        '//*[@id="btnRegister"]',
        '//*[@id="btnenroll"]',
        '//*[@id="btnEnroll"]',
        '//*[@id="btnregister"]',
    )
    for xpath in possible_xpaths:
        try:
            waited_find_element(driver=driver, by=By.XPATH, value=xpath).click()
            console.log("enroll button clicked!")
            return None
        except TimeoutException:
            continue

    console.log("ERROR: Unable to find the enroll button before timeout!")
    console.log("This is probably due to ASVZ changing their webpage layout.")
    console.log("Get in touch if this happens and I'll fix it.")


def enroll(
    driver,
    oe_time: datetime.datetime,
    url: str,
    asvz_id: str,
    asvz_password: str,
) -> None:
    while datetime.datetime.now() < oe_time - datetime.timedelta(seconds=30):
        time.sleep(2)
        console.log(
            f"Waiting to enroll for: {url} @ {oe_time} | {datetime.datetime.now()}"
        )

    print(f"Broken out of wait loop, time is: {datetime.datetime.now()}")
    print("Loading webpage...")
    driver.get(url)
    print("Clicking login buttons...")
    click_login_button(driver)
    login(driver, asvz_id=asvz_id, asvz_password=asvz_password)
    while True:
        time.sleep(0.01)
        if datetime.datetime.now() >= oe_time:
            print("Clicking enroll button...")
            click_enroll_button(driver)
            time.sleep(2)
            break
    print("Finished!")


def main():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    asvz_id = str(config["asvz_id"])
    asvz_password = str(config["asvz_password"])
    datetime_format = config["datetime_format"]
    urls = config["urls"]
    oe_times = config["enrollment_times"]  # online enrollment times
    assert len(urls) == len(oe_times), (
        "The number of URLs and enrollment times must be the same!"
        + f" But {len(urls)} urls found and {len(oe_times)} enrollment times found!"
    )
    # Convert to datetime objects
    oe_times = [
        datetime.datetime.strptime(oe_time, datetime_format) for oe_time in oe_times
    ]
    url_oe_time_pairs = list(zip(urls, oe_times))
    url_oe_time_pairs.sort(key=lambda pair: pair[1])  # Sort by date
    console.log("Config loaded!")
    console.log("Check the following is correct:")
    for url, oe_time in url_oe_time_pairs:
        console.log(f"Enrollment time: {oe_time} | URL: {url}")

    input("Press any key to continue...")
    while True:
        try:
            driver = instantiate_driver()
            for url, oe_time in url_oe_time_pairs:
                driver.get(url)
                enroll(
                    driver=driver,
                    oe_time=oe_time,
                    url=url,
                    asvz_id=asvz_id,
                    asvz_password=asvz_password,
                )

            time.sleep(100)
            driver.quit()
            console.log("Finished enrolling!")
            break
        except NoSuchWindowException:  # If we prematurely close the browser window
            console.log(
                "WARNING: Browser window was closed before the bot finished enrolling!"
            )
            console.log("Retrying...")
            time.sleep(2)


if __name__ == "__main__":
    main()
