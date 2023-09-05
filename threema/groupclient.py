import json
import logging
import requests


class GroupClient:
    def __init__(self, broadcastId, baseUrl, authHeader):
        self.broadcastId = broadcastId
        self.baseUrl = baseUrl
        self.authHeader = authHeader

    def getAllGroups(self, **params):
        url = f"{self.baseUrl}/identities/{self.broadcastId}/groups"

        resp = requests.get(url, params=params,
                            headers=self.authHeader)
        try:
            logging.info(f"Found content: {resp.content} for url {url}")
            data = json.loads(resp.content)
            logging.info(f"Found groups: {data}")
        except TypeError as te:
            logging.exception("Error while decoding:", te)
            return []
