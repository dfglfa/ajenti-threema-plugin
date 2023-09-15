import json
import logging
import time
import requests
import urllib

from .datamodel import User

USER_CACHE = {"timestamp": None, "users": []}


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
        now = int(time.time())
        if not USER_CACHE["timestamp"] or now - USER_CACHE["timestamp"] > 60:
            logging.info("Fetching all users from threema")
            url = f"{self.baseUrl}/users"

            # Not ideal performance-wise ... consider caching or fetching each user
            # record separately (= n requests for a class with n members)
            params = {"pageSize": 2000}

            resp = requests.get(
                url, params=params, headers=self.authHeader)

            data = json.loads(resp.content)
            users = data["users"]

            logging.info(f"**** Found {len(users)} users with credentials")
            users_with_creds = {self._extractCredsForUser(u): u for u in users}
            USER_CACHE["users"] = users_with_creds
            USER_CACHE["timestamp"] = now

        return USER_CACHE["users"]

    def _extractCredsForUser(self, user):
        for link in user["_links"]:
            if link.get("rel") == "credential":
                url = link["link"]
                creds_encoded = url.split("/credentials/")[-1]
                return urllib.parse.unquote(creds_encoded)
