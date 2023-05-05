import csv
import difflib
from operator import itemgetter
from datamodel import Credentials

from utils import getNameWithClassPrefix, sanitizeName


class NameMatcher:
    def __init__(self, csv_filename):
        self.nameToClass = {}
        self.normalized_names = []

        with open(csv_filename, "r") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=",")
            for rec in reader:
                key = sanitizeName(rec['Prenom'], rec['Nom'])
                cls = rec["Classe"]

                normalizedName = getNameWithClassPrefix(key, cls)
                self.normalized_names.append(normalizedName)
                self.nameToClass[normalizedName] = cls

        if len(self.nameToClass) != len(self.normalized_names):
            print(
                f"WARNING - Inconsistency detected: {len(self.nameToClass)} entries in class dict but {len(self.normalized_names)} normalized names found. Check list for duplicates!")

        print(
            f"**** Name database successfully initialized with {len(self.nameToClass)} entries ****")

    def findMatches(self, name) -> list:
        match = difflib.get_close_matches(
            name, self.nameToClass.keys(), 2, cutoff=0.8)
        if match:
            return [(res, self.nameToClass[res]) for res in match]
        else:
            return []

    def completeMatch(self, credentials: list[Credentials]):
        match_result = {
            "suggestions": {},
            "ok": [],
            "unmatched": [],
            "unused": []
        }
        mapped_keys = set()
        creds_keys = [c.asKey() for c in credentials]
        for ck in creds_keys:
            _, username = ck
            matches = self.findMatches(username)
            if not matches:
                match_result["unmatched"].append(ck)
            else:
                classOfFirstMatchWithPrefix = matches[0][1]
                if username.startswith(classOfFirstMatchWithPrefix):
                    # This username already has a matching prefix ...
                    # might be better to check if first and last name are already contained,
                    # but for now this is ok
                    match_result["ok"].append(ck)
                else:
                    match_result["suggestions"][ck] = matches
                mapped_keys = mapped_keys.union(map(itemgetter(0), matches))

        for nn in self.normalized_names:
            if nn not in mapped_keys:
                match_result["unused"].append(nn)

        return match_result
