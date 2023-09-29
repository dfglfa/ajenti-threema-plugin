import json
import logging
import requests


class GroupClient:
    def __init__(self, broadcastId, baseUrl, authHeader):
        self.broadcastId = broadcastId
        self.baseUrl = baseUrl
        self.authHeader = authHeader

    def getAllGroups(self):
        url = f"{self.baseUrl}/identities/{self.broadcastId}/groups"

        resp = requests.get(url, json={"states": ["active"]},
                            headers=self.authHeader)
        try:
            data = json.loads(resp.content)
            return data.get("groups", [])
        except TypeError as te:
            logging.exception("Error while decoding:", te)
            return []

    def getGroupMembers(self, groupId):
        url = f"{self.baseUrl}/identities/{self.broadcastId}/groups/{groupId}/members"

        resp = requests.get(url, headers=self.authHeader)
        try:
            data = json.loads(resp.content)
            return data.get("members", [])
        except TypeError as te:
            logging.exception("Error while decoding:", te)
            return []

    def getGroupDetails(self, groupId):
        url = f"{self.baseUrl}/identities/{self.broadcastId}/groups/{groupId}"
        resp = requests.get(url, headers=self.authHeader)
        return json.loads(resp.content)

    def createGroup(self, name, members):
        url = f"{self.baseUrl}/identities/{self.broadcastId}/groups"

        json = {"name": name, "members": members}
        logging.info(f"Sending a request to {url} with payload {json}")
        resp = requests.post(
            url, json=json, headers=self.authHeader)

        return "ok" if resp.status_code in [200, 204] else f"error: {resp.status_code}"

    def addGroupMembers(self, groupId, members):
        url = f"{self.baseUrl}/identities/{self.broadcastId}/groups/{groupId}"

        resp = requests.post(
            url, json={"members": members}, headers=self.authHeader)

        return "ok" if resp.status_code in [200, 204] else f"error: {resp.status_code}"
