import csv
import logging

from threema.utils import formatFirstname, formatLastname, formatName, normalizeClassName, normalizeName
from threema.config_loader import getStudentsFileName

try:
    from linuxmusterTools.ldapconnector import LMNLdapReader as ldapreader
except ImportError:
    ldapreader = None


class UserDataProvider():
    def getUserData(self):
        user_data = []
        if ldapreader:
            logging.info("Fetching user data via LDAP")
            user_data += ldapreader.get('/roles/student')
            user_data += ldapreader.get('/roles/teacher')
        else:
            filename = getStudentsFileName()
            logging.warn(
                f"Fetching user data from example data file {filename}")
            with open(filename, "r") as csv_file:
                reader = csv.DictReader(csv_file, delimiter=";")
                user_data = [{"sn": rec['Nom'], 
                              "givenName": rec['Prenom'],
                              "sAMAccountName": rec['sAMAccountName'],
                              "sophomorixAdminClass": rec["Classe"]} 
                              for rec in reader]

        active_users = [
            u for u in user_data if u["sophomorixAdminClass"].lower() != "attic"]

        user_dict = {}
        for user in active_users:
            user["cls"] = normalizeClassName(user["sophomorixAdminClass"])
            user["firstName"] = user["givenName"]
            user["lastName"] = user["sn"]
            user["normalizedName"] = normalizeName(formatName(user["firstName"], user["lastName"]), user["cls"])

            # Use ENT login as key
            user_dict[user["sAMAccountName"]] = user

        return user_dict
