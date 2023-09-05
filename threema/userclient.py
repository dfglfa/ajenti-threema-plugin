import json
import logging
import requests

from .datamodel import User


class UserClient:
    def __init__(self, baseUrl, authHeader):
        self.baseUrl = baseUrl
        self.authHeader = authHeader

    def getAll(self, **params):
        url = f"{self.baseUrl}/users"
        if "filterUsername" in params:
            url += f"?filterUsername={params['filterUsername']}"

        resp = requests.get(url, params=params,
                            headers=self.authHeader)
        try:
            print("*****************************", resp.content)
            data = json.loads(resp.content)
            users = data["users"]
            return [User(**u) for u in users]
        except TypeError as te:
            logging.exception("Error while decoding:", te)
            return []
