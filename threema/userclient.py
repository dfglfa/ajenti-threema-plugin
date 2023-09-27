import json
import logging
import time
import requests
import urllib

USER_CACHE = {"timestamp": None, "users": []}


class UserClient:
    def __init__(self, baseUrl, authHeader):
        self.baseUrl = baseUrl
        self.authHeader = authHeader

    def getAll(self, **params):
        now = int(time.time())
        if params or not USER_CACHE["timestamp"] or now - USER_CACHE["timestamp"] > 60:
            logging.info("Fetching all users from threema")
            url = f"{self.baseUrl}/users"

            if "pageSize" not in params:
                params["pageSize"] = 2000

            resp = requests.get(
                url, params=params, headers=self.authHeader)

            data = json.loads(resp.content)
            users = data["users"]

            if params.get("filterIds"):
                users = [u for u in users if u["id"] in params["filterIds"]]

            # Set credentials attribute on each user
            for u in users:
                u["credentials_id"] = self._extractCredsForUser(u)
            USER_CACHE["users"] = users
            USER_CACHE["timestamp"] = now

        return USER_CACHE["users"]

    def _extractCredsForUser(self, user):
        for link in user["_links"]:
            if link.get("rel") == "credential":
                url = link["link"]
                creds_encoded = url.split("/credentials/")[-1]
                return urllib.parse.unquote(creds_encoded)
