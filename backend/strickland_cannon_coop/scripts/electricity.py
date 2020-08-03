import datetime
import pathlib
import json


import requests

import tqdm

from strickland_cannon_coop.settings import ELECTRICITY


def _main(prev_results):
    usage_data = prev_results["usageData"]
    prev_datetime = usage_data[-1][0] if usage_data else "2018-10-01@12:00 am"
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


def _get_json_path():
    existing = pathlib.Path("../data/electricity.json")
    if not existing.exists():
        existing.write_text(json.dumps({"usageData": []}))

    return existing


def main():
    json_file = _get_json_path()
    prev_results = json.loads(json_file.read_text())
    results = _main(prev_results)
    json_file.write_text(json.dumps(results))


if __name__ == "__main__":
    main()
