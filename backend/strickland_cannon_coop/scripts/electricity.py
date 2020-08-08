import datetime

import requests

import tqdm

from strickland_cannon_coop.utils import gpgjson
from strickland_cannon_coop.settings import ELECTRICITY, START_DATE


def _main(prev_results):
    usage_data = prev_results["usageData"]
    prev_datetime = usage_data[-1][0] if usage_data else f"{START_DATE}@12:00 am"
    prev_datestamp = prev_datetime.split("@")[0]
    prev_date = datetime.datetime.strptime(prev_datestamp, r"%Y-%m-%d").date()
    while usage_data and usage_data[-1][0].startswith(prev_datestamp):
        usage_data.pop()

    response = requests.post(
        "https://smartmetertexas.com/api/user/authenticate",
        verify=False,
        data={
            "username": ELECTRICITY["username"],
            "password": ELECTRICITY["password"],
            "rememberMe": "true",
        },
    )
    token = response.json()["token"]

    for date_offset in tqdm.tqdm(range((datetime.date.today() - prev_date).days)):
        date = prev_date + datetime.timedelta(days=date_offset)
        response = requests.post(
            "https://smartmetertexas.com/api/usage/interval",
            verify=False,
            headers={"authorization": f"Bearer {token}"},
            data={
                "esiid": ELECTRICITY["esiid"],
                "startDate": date.strftime(r"%m/%d/%Y"),
                "endDate": date.strftime(r"%m/%d/%Y"),
            },
        )
        interval_data = response.json()["intervaldata"]
        for datum in interval_data:
            usage_data.append(
                (f"{datum['date']}@{datum['starttime'][1:]}", datum["consumption"])
            )

    return prev_results


def _get_gpgjson_file():
    gpgjson_file = gpgjson.GPGJsonFile("../data/electricity.json")
    if not gpgjson_file.exists():
        gpgjson_file.write({"usageData": []})
    else:
        print(gpgjson_file._path.read_text())

    return gpgjson_file


def main():
    gpgjson_file = _get_gpgjson_file()
    prev_results = gpgjson_file.read()
    results = _main(prev_results)
    gpgjson_file.write(results)


if __name__ == "__main__":
    main()
