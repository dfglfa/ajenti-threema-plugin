import json
import logging
import random
import string
import requests

from .datamodel import Credentials
from .datamodel import User
from .namematcher import NameMatcher
from urllib.parse import quote
from .config_loader import getStudentsFileName
import os
from aj.api.endpoint import EndpointError

GRADES_NAMES_COLLEGE_GERMAN = range(5, 10)
GRADES_NAMES_COLLEGE_FRENCH = range(6, 2, -1)
GRADES_COLLEGE_GERMAN = [f"{g}a" for g in GRADES_NAMES_COLLEGE_GERMAN] + \
    [f"{g}b" for g in GRADES_NAMES_COLLEGE_GERMAN]
GRADES_COLLEGE_FRENCH = [f"{g}I" for g in GRADES_NAMES_COLLEGE_FRENCH] + \
    [f"{g}II" for g in GRADES_NAMES_COLLEGE_FRENCH]
GRADES_LYCEE = ["2ES", "2L1", "2L2", "2S1", "2S2", "1ES", "1L1", "1L2",
                "1SBC1", "1SBC2", "1SMP", "TES", "TL1", "TL2", "TSBC1", "1TSBC2", "TSMP"]
GRADES = GRADES_COLLEGE_GERMAN + GRADES_COLLEGE_FRENCH + GRADES_LYCEE


class CredentialsClient:
    def __init__(self, baseUrl: str, authHeader: dict):
        self.baseUrl = baseUrl
        self.authHeader = authHeader

        students_data_file = os.path.join(os.getcwd(), getStudentsFileName())
        self.nameMatcher = NameMatcher(students_data_file)

    def getAllMocked(self, **params):
        students = []
        with open("threema_dummy_data.csv") as data:
            for line in data:
                sid = random.randint(10 ** 5, 10 ** 10)
                username = line.split(",")[0]
                students.append({"id": sid, "username": username})
        return [Credentials(**c) for c in students]

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
