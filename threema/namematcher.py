import difflib
import logging
from operator import itemgetter

from threema.datamodel import Credentials
from threema.utils import CLASS_TO_LEVEL


CLASS_NAMES = CLASS_TO_LEVEL.keys()


class NameMatcher:
    def __init__(self, userdata_provider):
        self.prefixedNameToClass = {}
        self.formattedNameToClass = {}
        self.normalized_names = []

        user_data = userdata_provider.getUserData()

        for user in user_data:
            self.normalized_names.append(user["normalizedName"])
            self.prefixedNameToClass[user["normalizedName"]] = user["cls"]
            self.formattedNameToClass[user["formattedName"]] = user["cls"]

        if len(self.prefixedNameToClass) != len(self.normalized_names):
            logging.warn(
                f"WARNING - Inconsistency detected: {len(self.prefixedNameToClass)} entries in class dict but {len(self.normalized_names)} normalized names found. Check list for duplicates!")

        logging.info(
            f"**** Name database successfully initialized with {len(self.prefixedNameToClass)} entries ****")

    def findMatches(self, name) -> list:
        studentName = self._extractStudentName(name)
        logging.info(f"Extracted {studentName} from {name}")

        if studentName in self.formattedNameToClass:
            cls = self.formattedNameToClass[studentName]
            return [(f"{cls}_{studentName}", cls)]

        return self._findFuzzyMatches(name)

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
            if username in self.normalized_names:
                matches = [(username, self.prefixedNameToClass[username])]
                logging.info(f"Found exact match for {username}")
                match_result["ok"].append(
                    {"id": threemaId, "username": username})
            else:
                matches = self.findMatches(username)
                if not matches:
                    if self._extractStudentName(username) != username:
                        match_result["unmatched"].append(
                            {"id": threemaId, "username": username})
                    continue
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

    def _findFuzzyMatches(self, name) -> list:
        match = difflib.get_close_matches(
            name, self.prefixedNameToClass.keys(), 2, cutoff=0.8)
        if match:
            logging.info(f"Found fuzzy match for {name}")
            return [(res, self.prefixedNameToClass[res]) for res in match]
        else:
            return []

    def _extractStudentName(self, rawName):
        if "_" in rawName:
            return rawName.split("_", 1)[1]
        for cn in list(CLASS_NAMES) + ["6II", "6I", "5II", "5I", "4II", "4I", "3II", "3I"]:
            if rawName.lower().startswith(cn.lower()):
                return rawName[len(cn):]
        return rawName
