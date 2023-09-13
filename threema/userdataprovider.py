import csv
import logging

from .config_loader import getStudentsFileName

try:
    from aj.plugins.lmn_common.ldap.requests import LMNLdapRequests
except ImportError:
    LMNLdapRequests = None


class UserDataProvider():
    def getUserData(self):
        user_data = []
        if LMNLdapRequests:
            logging.info("Fetching user data via LDAP")
            lr = LMNLdapRequests(None)
            user_data += lr.get('/role/student', school_oriented=False)
            user_data += lr.get('/role/teacher', school_oriented=False)
        else:
            filename = getStudentsFileName()
            logging.warn(
                f"Fetching user data from example data file {filename}")
            with open(filename, "r") as csv_file:
                reader = csv.DictReader(csv_file, delimiter=",")
                return [{"sn": rec['Nom'], "givenName": rec['Prenom'], "sophomorixAdminClass": rec["Classe"]} for rec in reader]
        return user_data
