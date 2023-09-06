import json
import logging
import requests
import urllib

from .datamodel import User


class UserClient:
    def __init__(self, baseUrl, authHeader):
        self.baseUrl = baseUrl
        self.authHeader = authHeader

    def getAll(self, **params):
        url = f"{self.baseUrl}/users"
        if params.get("filterUsername"):
            url += f"?filterUsername={params['filterUsername']}"

        resp = requests.get(url, params=params,
                            headers=self.authHeader)
        try:
            data = json.loads(resp.content)
            users = data["users"]
            return [User(**u) for u in users]
        except TypeError as te:
            logging.exception("Error while decoding:", te)
            return []

    def getUsersWithLinkedCredentials(self):
        url = f"{self.baseUrl}/users"
        resp = requests.get(url, headers=self.authHeader)

        data = json.loads(resp.content)
        users = data["users"]

        print(users)

        return {self._extractCredsForUser(u): u for u in users}

    def _extractCredsForUser(self, user):
        for link in user["_links"]:
            if link.get("rel") == "credential":
                url = link["link"]
                creds_encoded = url.split("/credentials/")[-1]
                return urllib.parse.unquote(creds_encoded)
