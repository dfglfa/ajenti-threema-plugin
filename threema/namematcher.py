import csv
import difflib
import logging
from operator import itemgetter

from .config_loader import getStudentsFileName

from .datamodel import Credentials

from .utils import normalizeName, sanitizeName
from aj.plugins.lmn_common.ldap.requests import LMNLdapRequests


class NameMatcher:
    def __init__(self):
        self.nameToClass = {}
        self.normalized_names = []

        try:
            logging.info("Accessing user data via LDAP")
            lr = LMNLdapRequests(None)

            users_data = lr.get('/role/student', school_oriented=False)
            users_data += lr.get('/role/teacher', school_oriented=False)

            for user in users_data:
                key = sanitizeName(user['givenName'], user['sn'])
                cls = user["sophomorixAdminClass"]

                normalizedName = normalizeName(key, cls)
                self.normalized_names.append(normalizedName)
                self.nameToClass[normalizedName] = cls
        except Exception as ex:
            logging.error("Could not fetch user via LDAP", ex)
            logging.warn("Falling back to dummy data from csv")

            with open(getStudentsFileName(), "r") as csv_file:
                reader = csv.DictReader(csv_file, delimiter=",")
                for rec in reader:
                    key = sanitizeName(rec['Prenom'], rec['Nom'])
                    cls = rec["Classe"]

                    normalizedName = normalizeName(key, cls)
                    self.normalized_names.append(normalizedName)
                    self.nameToClass[normalizedName] = cls

        if len(self.nameToClass) != len(self.normalized_names):
            logging.warn(
                f"WARNING - Inconsistency detected: {len(self.nameToClass)} entries in class dict but {len(self.normalized_names)} normalized names found. Check list for duplicates!")

        logging.info(
            f"**** Name database successfully initialized with {len(self.nameToClass)} entries ****")

    def findMatches(self, name) -> list:
        match = difflib.get_close_matches(
            name, self.nameToClass.keys(), 2, cutoff=0.8)
        if match:
            return [(res, self.nameToClass[res]) for res in match]
        else:
            return []

    def checkConsistency(self, credentials: list[Credentials]):
        match_result = {
            "suggestions": [],
            "ok": [],
            "unmatched": [],
            "unused": []
        }
        mapped_keys = set()
        creds_keys = [(c.id, c.username or "unknown") for c in credentials]
        for threemaId, username in creds_keys:
            matches = self.findMatches(username)
            if not matches:
                match_result["unmatched"].append(
                    {"id": threemaId, "username": username})
            else:
                if username == matches[0][0]:
                    logging.debug(
                        f"User name {username} matches {matches[0][0]}")
                    match_result["ok"].append(
                        {"id": threemaId, "username": username})
                elif username.startswith(matches[0][1]):
                    # If the first match contains the correct class, suggest
                    # only this match and no others.
                    match_result["suggestions"].append({
                        "id": threemaId, "username": username, "matches": matches[:1]
                    })
                else:
                    match_result["suggestions"].append({
                        "id": threemaId, "username": username, "matches": matches
                    })
                mapped_keys = mapped_keys.union(map(itemgetter(0), matches))

        for nn in self.normalized_names:
            if nn not in mapped_keys:
                match_result["unused"].append(nn)

        match_result["unused"].sort()
        match_result["suggestions"].sort(key=lambda s: s["username"])

        # Make sure no validated names appear as suggestions
        all_ok_names = [u["username"] for u in match_result["ok"]]
        for sugg in match_result["suggestions"]:
            sugg["matches"] = [
                sm for sm in sugg["matches"] if sm[0] not in all_ok_names]
            if not sugg["matches"]:
                match_result["unmatched"].append(
                    {"id": sugg["id"], "username": sugg["username"]})
        match_result["suggestions"] = [
            mr for mr in match_result["suggestions"] if mr["matches"]]

        return match_result
