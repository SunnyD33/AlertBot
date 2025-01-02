import json
import logging
import os

import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()
TOKEN = str(os.getenv("BOT_TOKEN"))

apiVer = 10  # Will need to update with api version changes as needed


class User:
    def getUserID(self, userid):
        try:
            url = "https://discord.com/api/v{}/users/{}".format(apiVer, userid)
            header = {
                "Content-Type": "application/json",
                "Authorization": "Bot {}".format(TOKEN),
            }
            response = requests.get(url, headers=header)
            response.raise_for_status()

            logging.info("Response Details")
            logging.info("-----------------")
            logging.info(f"Request URL: {response.url}")
            logging.info(f"Status Code: {response.status_code}")
            # logging.info(f"Response Headers: {response.headers}")

            json_data = json.loads(response.text)
            # print(json_data)

            if "global_name" in json_data:
                if json_data["global_name"] is None:
                    return json_data["username"] + ": " + json_data["id"]
                else:
                    return json_data["global_name"] + ": " + json_data["id"]
            elif "global_name" not in json_data:
                return json_data["username"] + ": " + json_data["id"]
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)

    def getUserGuild(self, guildId):
        try:
            url = "https://discord.com/api/v{}/guilds/{}".format(
                apiVer, guildId
            )
            header = {
                "Content-Type": "application/json",
                "Authorization": "Bot {}".format(TOKEN),
            }
            response = requests.get(url, headers=header)
            response.raise_for_status()

            logging.info("Response Details")
            logging.info("-----------------")
            logging.info(f"Request URL: {response.url}")
            logging.info(f"Status Code: {response.status_code}")
            # logging.info(f"Response Headers: {response.headers}")

            json_data = json.loads(response.text)
            # print(json_data)

            return json_data["name"]
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
