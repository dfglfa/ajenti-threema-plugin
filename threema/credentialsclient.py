import json
import logging
import random
import string
import requests


from threema.entuserdataprovider import ENTUserDataProvider

from threema.datamodel import Credentials, User
from threema.utils import CLASS_TO_LEVEL

from urllib.parse import quote
from aj.api.endpoint import EndpointError

GRADES = CLASS_TO_LEVEL.keys()


class CredentialsClient:
    def __init__(self, baseUrl: str, authHeader: dict):
        self.baseUrl = baseUrl
        self.authHeader = authHeader
        self.ENTUserDataProvider = ENTUserDataProvider()

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

            if params.get("json"):
                return credentialsList

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
        userForEntLogin = self.ENTUserDataProvider.getUserData()
        threemaCredentialsForCredsName = self.getCredsByName()
        
        result = {
            "matched": [],
            "unmatched": [],
            "unused": []
        }

        matchedThreemaIds = []
        unmatchedEntLogins = []
        for entLogin, userdata in userForEntLogin.items():
            std_name = userdata["standardThreemaName"]
            if std_name in threemaCredentialsForCredsName:
                # Exact match found => set credentials ID in ENT user dict
                credsId = threemaCredentialsForCredsName[std_name].id
                userForEntLogin[entLogin]["credsId"] = credsId
                userForEntLogin[entLogin]["currentThreemaLogin"] = std_name
                userForEntLogin[entLogin]["correctThreemaLogin"] = std_name
                result["matched"].append(userForEntLogin[entLogin])
                matchedThreemaIds.append(credsId)
            else:
                # There is no exact threema login match for this ENT user
                unmatchedEntLogins.append(entLogin)

        prefixLessThreemaCreds = {cname.split("_")[-1]: data for cname, data in threemaCredentialsForCredsName.items()}
        for unmatchedEntLogin in unmatchedEntLogins:
            normedName = userForEntLogin[unmatchedEntLogin]["normalizedName"]
            logging.info(f"ENT login {unmatchedEntLogin} has no corresponding threema user, now checking {normedName}")
            if normedName in threemaCredentialsForCredsName:
                logging.info(f"Found old-style threema login {normedName}")
                credsId = threemaCredentialsForCredsName[normedName].id
                userForEntLogin[unmatchedEntLogin]["credsId"] = credsId
                userForEntLogin[unmatchedEntLogin]["currentThreemaLogin"] = normedName
                userForEntLogin[unmatchedEntLogin]["correctThreemaLogin"] = userForEntLogin[unmatchedEntLogin]["standardThreemaName"]
                result["matched"].append(userForEntLogin[unmatchedEntLogin])
                matchedThreemaIds.append(credsId)
            elif unmatchedEntLogin in threemaCredentialsForCredsName:
                logging.info(f"Found plain ENT login {unmatchedEntLogin} as threema login => prefix needed")
                credsId = threemaCredentialsForCredsName[unmatchedEntLogin].id
                userForEntLogin[unmatchedEntLogin]["credsId"] = credsId
                userForEntLogin[unmatchedEntLogin]["currentThreemaLogin"] = unmatchedEntLogin
                userForEntLogin[unmatchedEntLogin]["correctThreemaLogin"] = userForEntLogin[unmatchedEntLogin]["standardThreemaName"]
                result["matched"].append(userForEntLogin[unmatchedEntLogin])
                matchedThreemaIds.append(credsId)
            elif unmatchedEntLogin.split("_")[-1] in prefixLessThreemaCreds:
                logging.info(f"Found ENT login {unmatchedEntLogin} with wrong prefix => prefix change needed")
                raw_login = unmatchedEntLogin.split("_")[-1]
                credsId = prefixLessThreemaCreds[raw_login].id
                userForEntLogin[unmatchedEntLogin]["credsId"] = credsId
                userForEntLogin[unmatchedEntLogin]["currentThreemaLogin"] = unmatchedEntLogin
                userForEntLogin[unmatchedEntLogin]["correctThreemaLogin"] = userForEntLogin[unmatchedEntLogin]["standardThreemaName"]
                result["matched"].append(userForEntLogin[unmatchedEntLogin])
                matchedThreemaIds.append(credsId)
            else:
                result["unused"].append(unmatchedEntLogin)
        
        for threemaName in threemaCredentialsForCredsName:
            credsId = threemaCredentialsForCredsName[threemaName].id
            if credsId not in matchedThreemaIds:
                result["unmatched"].append({"id": credsId, "username": threemaName})

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
