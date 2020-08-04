import datetime
import decimal
import json

from dateutil import relativedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as expected_conditions

from strickland_cannon_coop.utils import gpgjson
from strickland_cannon_coop.settings import MORTGAGE


def _load_cookies():
    with open("mortgage.cookies") as cookies_file:
        return json.load(cookies_file)


def _parse_money(text):
    return decimal.Decimal(text.lstrip("$").replace(",", ""))


def _calulate_months(payment, loan, rate):
    return (payment / (payment - rate * loan)).log10() / (rate + 1).log10()


def _load_results(rows):
    paymentMonth = None
    principals = []
    interests = []

    for row in list(rows)[1::2]:
        data = row.find_elements_by_tag_name("td")

        if data[3].text == "Loan Set-Up":
            originalAmount = _parse_money(data[9].text)
            continue

        principal = _parse_money(data[4].text)
        interest = _parse_money(data[5].text)

        if interest:  # A mortgage payment 🎉
            if paymentMonth is None:
                paymentMonth = datetime.datetime.strptime(data[1].text, r"%m/%d/%Y")
                firstPaymentDate = paymentMonth.strftime(r"%m/%Y")
            else:
                paymentMonth = paymentMonth + relativedelta.relativedelta(months=1)

            principals.append(principal)
            interests.append(interest)
        elif principal:
            principals[-1] += principal

    first_payment = principals[0] + interests[0]
    monthly_interest_rate = interests[0] / originalAmount
    return {
        "firstPaymentDate": firstPaymentDate,
        "originalAmount": str(originalAmount.to_integral_value()),
        "termInMonths": str(
            _calulate_months(
                first_payment, originalAmount, monthly_interest_rate
            ).to_integral_value()
        ),
        "interestRateInPercent": str((monthly_interest_rate * 1200).normalize()),
        "principal": list(map(str, principals)),
        "interest": list(map(str, interests)),
    }


def _main(driver):
    driver.get("https://www.loanadministration.com/")

    for cookie in _load_cookies():
        driver.add_cookie(cookie)

    driver.find_element_by_id("page:form:un").send_keys(MORTGAGE["username"])
    driver.find_element_by_id("page:form:password").send_keys(MORTGAGE["password"])
    driver.find_element_by_id("page:form:Login").click()
    webdriver.support.ui.WebDriverWait(driver, 10).until(
        expected_conditions.title_is("Welcome")
    )

    driver.get("https://www.loanadministration.com/apex/BKFSPage?target=LA")

    webdriver.support.ui.WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.ID, "DATERANGE"))
    )
    webdriver.support.select.Select(
        driver.find_element_by_id("DATERANGE")
    ).select_by_value("ALL")

    buttons = driver.find_elements_by_tag_name("button")
    for button in buttons:
        if button.text == "Search":
            break
    button.click()

    webdriver.support.select.Select(driver.find_element_by_id("TRAN")).select_by_value(
        "LNACTTYPAY"
    )

    for button in buttons:
        if button.text == "Filter":
            break
    button.click()

    rows = []
    while len(rows) < 10:
        table = driver.find_element_by_id("la-expander")
        table_body = table.find_elements_by_tag_name("tbody")[0]
        rows = table_body.find_elements_by_tag_name("tr")

    return _load_results(reversed(rows))


def main():
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    try:
        results = _main(driver)
    finally:
        driver.close()

    dest = gpgjson.GPGJsonFile("../data/mortgage.json")
    dest.write(results)


if __name__ == "__main__":
    main()
