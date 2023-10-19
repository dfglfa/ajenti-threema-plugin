import csv
import logging

from .utils import formatFirstname, formatLastname, formatName, normalizeClassName, normalizeName
from .config_loader import getStudentsFileName

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
                user_data = [{"sn": rec['Nom'], "givenName": rec['Prenom'],
                              "sophomorixAdminClass": rec["Classe"]} for rec in reader]

        active_users = [
            u for u in user_data if u["sophomorixAdminClass"].lower() != "attic"]

        for user in active_users:
            formattedName = formatName(user['givenName'], user['sn'])
            user["formattedName"] = formattedName

            cls = normalizeClassName(user["sophomorixAdminClass"])
            user["cls"] = cls

            user["normalizedName"] = normalizeName(formattedName, cls)

            user["givenName"] = formatFirstname(user["givenName"])
            user["sn"] = formatLastname(user["sn"])
            user["originalLastname"] = user["sn"]

        return active_users
