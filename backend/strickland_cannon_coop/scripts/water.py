import datetime
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.expected_conditions as expected_conditions

import requests

import tqdm

from strickland_cannon_coop.utils import gpgjson
from strickland_cannon_coop.settings import WATER, START_DATE


def _get_request_cookies(driver):
    driver.get("https://waterbilling.arlingtontx.gov/app/login.jsp")
    driver.find_element_by_xpath('//*[@id="prefix-overlay-header"]/button').click()
    driver.find_element_by_id("accessCode").send_keys(WATER["username"])
    driver.find_element_by_id("password").send_keys(WATER["password"])
    driver.find_element_by_id("password").send_keys(Keys.RETURN)
    return driver.get_cookies()


def _get_results(cookies, prev_results):
    usage_data = prev_results["usageData"]
    # @TODO: Don't hardcode!
    start_datestamp = usage_data[-1][0] if usage_data else START_DATE
    start_date = datetime.datetime.strptime(start_datestamp, r"%Y-%m-%d").date()
    while usage_data and usage_data[-1][0].startswith(start_datestamp):
        usage_data.pop()

    max_step_size = 90
    num_days = (datetime.date.today() - start_date).days
    day_offset_starts = list(range(num_days))[::max_step_size]

    for day_offset_start in tqdm.tqdm(day_offset_starts):
        start = start_date + datetime.timedelta(days=day_offset_start)
        num_days_offset = min(max_step_size, num_days - day_offset_start)
        end = start + datetime.timedelta(days=num_days_offset - 1)

        response = requests.post(
            "https://waterbilling.arlingtontx.gov/app/capricorn?para=smartMeterConsum"
            "&inquiryType=water"
            f"&fromYear={start.year}&fromMonth={start.month}&fromDay={start.day}"
            f"&toYear={end.year}&toMonth={end.month}&toDay={end.day}",
            cookies={cookie["name"]: cookie["value"] for cookie in cookies},
        )

        # Having to parse HTML/JS response :grimacing:
        usage_index = response.text.find('name: "Usage",')
        data_start_index = response.text.find("data: ", usage_index) + 5
        data_end_index = response.text.find("\n", data_start_index) - 2
        data_str = response.text[data_start_index:data_end_index].strip()

        data = json.loads(data_str)
        assert len(data) == num_days_offset
        for index, datum in enumerate(data):
            date = start + datetime.timedelta(days=index)
            usage_data.append((f"{date.strftime(r'%Y-%m-%d')}", datum))

    return prev_results


def _get_gpgjson_file():
    gpgjson_file = gpgjson.GPGJsonFile("../data/water.json")
    if not gpgjson_file.exists():
        gpgjson_file.write({"usageData": []})

    return gpgjson_file


def main():
    gpgjson_file = _get_gpgjson_file()
    prev_results = gpgjson_file.read()

    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    try:
        cookies = _get_request_cookies(driver)
    finally:
        driver.close()

    results = _get_results(cookies, prev_results)

    gpgjson_file.write(results)


if __name__ == "__main__":
    main()
