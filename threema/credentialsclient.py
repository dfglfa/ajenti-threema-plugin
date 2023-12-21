import json
import logging
import random
import string
import requests


from threema.userdataprovider import UserDataProvider

from threema.datamodel import Credentials, User
from threema.utils import formatName, normalizeName, CLASS_TO_LEVEL

from urllib.parse import quote
from aj.api.endpoint import EndpointError

GRADES = CLASS_TO_LEVEL.keys()


class CredentialsClient:
    def __init__(self, baseUrl: str, authHeader: dict):
        self.baseUrl = baseUrl
        self.authHeader = authHeader
        self.userDataProvider = UserDataProvider()

    def getAll(self, **params):
        url = f"{self.baseUrl}/credentials"

        req_params = params
        params["pageSize"] = 1000

        resp = requests.get(url, params=req_params, headers=self.authHeader)

        if resp.status_code >= 400:
            self._handleError(resp)
            return []

        try:
            data = json.loads(resp.content)
            credentialsList = data["credentials"]
            return [Credentials(**c) for c in credentialsList]
        except TypeError as te:
            logging.exception(f"Error while decoding: {te}")
            return []

    def create(self, username: str, password: str) -> User:
        url = f"{self.baseUrl}/credentials"
        resp = requests.post(url, json={"username": username,
                                        "password": password or self._get_random_password()},
                             headers=self.authHeader)

        if resp.status_code >= 400:
            self._handleError(resp)
            return []

        try:
            data = json.loads(resp.content)
            user = User(**data)
            logging.info(f"Successfully created new user: {user}")
        except TypeError as te:
            logging.exception(f"Error while decoding: {te}")
            return []

    def getDetails(self, threemaId):
        url = self._getUrlForId(threemaId)
        resp = requests.get(url, headers=self.authHeader)

        if resp.status_code >= 400:
            self._handleError(resp)
            return []

        try:
            data = json.loads(resp.content)
            return Credentials(**data)
        except TypeError as te:
            logging.exception(f"Error while decoding: {te}")
            return []

    def update(self, threemaId, username, password):
        url = self._getUrlForId(threemaId)

        if not password:
            # Need to fetch password, as it should stay unchanged
            details = self.getDetails(threemaId)
            password = details.password

        resp = requests.put(url, json={"id": threemaId, "username": username, "password": password},
                            headers=self.authHeader)

        if resp.status_code >= 400:
            self._handleError(resp)

        if resp.status_code == 204:
            logging.info("User successfully updated")
        else:
            logging.error(f"Response {resp.status_code}. Please check again.")
    
    def deleteCredentials(self, threemaId):
        url = self._getUrlForId(threemaId)
        resp = requests.delete(url, headers=self.authHeader)

        if resp.status_code >= 400:
            self._handleError(resp)
            return []

        if resp.status_code == 204:
            logging.info(
                f"Credentials for threema ID {threemaId} successfully deleted")
        else:
            logging.error(f"Response {resp.status_code}. Please check again.")

    def matchAgainstMasterUserData(self):
        master_user_dict = self.userDataProvider.getUserData()
        threema_creds_dict = self.getCredsByName()
        
        result = {
            "suggestions": [],
            "ok": [],
            "unmatched": [],
            "unused": []
        }

        unhandledMuids = []
        for muid in master_user_dict:
            print("Checking ", muid, "in ent creds")
            if muid not in threema_creds_dict:
                unhandledMuids.append(muid)
            else:
                result["ok"].append(muid)

        matchedThreemaIds = []
        for umu in unhandledMuids:
            normedName = master_user_dict[umu]["normalizedName"]
            if normedName in threema_creds_dict:
                matchedThreemaIds.append(normedName)
                print(f"Found old format {normedName} for ent ID {umu} (threemaId {threema_creds_dict[normedName].id})")
                result["suggestions"].append(
                    {"id": threema_creds_dict[normedName].id, "username": normedName, "matches": umu})
            else:
                result["unmatched"].append({"id": umu})
        
        for threemaName in threema_creds_dict:
            if threemaName not in matchedThreemaIds:
                result["unused"].append(threemaName)

        return result


    def getCredsByName(self):
        return {c.username: c for c in self.getAll()}


    def _getUrlForId(self, threemaId):
        return f"{self.baseUrl}/credentials/{quote(threemaId, safe='')}"

    def _get_random_password(self):
        return "".join(random.choice(string.ascii_letters) for _ in range(8))

    def _handleError(self, response):
        try:
            content = json.loads(response.content)
            message = content["error"]
        except Exception:
            message = "No content"
        logging.error(f"Error code {response.status_code}: {message}")
        raise EndpointError(
            f"Error code {response.status_code}: {message}")
