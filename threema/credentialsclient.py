import json
import logging
import random
import string
import requests


from threema.userdataprovider import UserDataProvider

from threema.datamodel import Credentials, User
from threema.namematcher import NameMatcher
from threema.utils import formatName, normalizeName, CLASS_TO_LEVEL

from urllib.parse import quote
from aj.api.endpoint import EndpointError

GRADES = CLASS_TO_LEVEL.keys()


class CredentialsClient:
    def __init__(self, baseUrl: str, authHeader: dict):
        self.baseUrl = baseUrl
        self.authHeader = authHeader
        self.nameMatcher = NameMatcher(UserDataProvider())

    def getAll(self, **params):
        url = f"{self.baseUrl}/credentials"

        req_params = params
        params["pageSize"] = 1000

        resp = requests.get(url, params=req_params, headers=self.authHeader)

        if resp.status_code >= 400:
            self._handleError(resp)
            return []

        filter_prefix = f"{params['classname']}_" if params.get(
            "classname") else ""
        try:
            data = json.loads(resp.content)
            credentialsList = data["credentials"]
            return [Credentials(**c) for c in credentialsList if c["username"].startswith(filter_prefix)]
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

    def checkNamingScheme(self) -> dict:
        creds = self.getAll()
        stats = {
            "creds_total": len(creds),
            "ok": 0,
            "not_ok": []
        }
        for cred in creds:
            if self._matchesNamingScheme(cred):
                stats["ok"] += 1
            else:
                stats["not_ok"].append(
                    (cred.id, cred.username or "<EMPTY_USERNAME>"))

        return stats

    def correctNamingScheme(self):
        candidates = self.checkNamingScheme()["not_ok"]

        logging.debug(f"Checking {len(candidates)} values for correction")
        res = {
            "suggestions": {},
            "notFixable": []
        }
        for candidate in candidates:
            _, username = candidate
            matches = self.nameMatcher.findMatches(username)
            if matches:
                res["suggestions"][candidate] = [
                    f"{cls}_{match}" for match, cls in matches]
            else:
                res["notFixable"].append(candidate)

        return res

    def findMatchesForRecords(self, records):
        creds = self.getAll()
        matches = []
        for r in records:
            normalizedName = normalizeName(formatName(
                r["firstName"], r["lastName"]), r["class"])
            logging.info(f"Searching for normalized name {normalizedName}")
            for c in creds:
                if c.username == normalizedName:
                    logging.info(f"Found match with ID {c.id}")
                    matches.append(c)
                    break

        return matches

    def checkConsistencyForAllStudents(self):
        return self.nameMatcher.checkConsistency(self.getAll())

    def checkConsistencyForStudentIds(self, threemaIds):
        if len(threemaIds) > 5:
            # pretty random cutoff ... idea: for more than 5 ids it might be more
            # efficient to just fetch all creds and apply a filter on those.
            filtered = [c for c in self.getAll() if c.id in threemaIds]
        else:
            filtered = [self.getDetails(tid) for tid in threemaIds]
        return self.nameMatcher.checkConsistency(filtered)

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

    def _getUrlForId(self, threemaId):
        return f"{self.baseUrl}/credentials/{quote(threemaId, safe='')}"

    def _matchesNamingScheme(self, cred: Credentials) -> bool:
        for prefix in GRADES:
            if cred.username and cred.username.startswith(prefix):
                return True
        return False

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
