import json
import requests

from .datamodel import User


class UserClient:
    def __init__(self, baseUrl, authHeader):
        self.baseUrl = baseUrl
        self.authHeader = authHeader

    def getAll(self, **params):
        url = f"{self.baseUrl}/users"

        resp = requests.get(url, params=params,
                            headers=self.authHeader)
        try:
            data = json.loads(resp.content)
            users = data["users"]
            return [User(**u) for u in users]
        except TypeError as te:
            print("Error while decoding:", te)
            return []
