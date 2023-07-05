
import logging


try:
    from .config import API_KEY
except ImportError:
    logging.error("*" * 50)
    logging.error("WARNING: API_KEY not readable from config.py")
    logging.error(
        "Please rename _config.py -> config.py and insert your API key there.")
    logging.error("Threema access will not work otherwise.")
    logging.error("*" * 50)
    API_KEY = ""

from .credentialsclient import CredentialsClient
from .userclient import UserClient


DEFAULT_BASE_URL = "https://work.threema.ch/api/v1"
AUTH_HEADER = {"X-Api-Key": API_KEY}


class ThreemaAdminClient:

    def __init__(self, baseUrl=DEFAULT_BASE_URL):
        self.baseUrl = baseUrl
        self.userClient = UserClient(baseUrl, AUTH_HEADER)
        self.credentialsClient = CredentialsClient(
            baseUrl, AUTH_HEADER)

    def getAllUsers(self, **params):
        return self.userClient.getAll(**params)

    def getAllCredentials(self, **params):
        return self.credentialsClient.getAll(**params)

    def createCredentials(self, username, password):
        return self.credentialsClient.create(username, password)

    def checkCredentialsNamingScheme(self):
        return self.credentialsClient.checkNamingScheme()

    def correctCredentialsNamingScheme(self):
        return self.credentialsClient.correctNamingScheme()

    def checkConsistencyForAllStudents(self):
        return self.credentialsClient.checkConsistencyForAllStudents()

    def checkConsistencyForStudentIds(self, threemaIds):
        return self.credentialsClient.checkConsistencyForStudentIds(threemaIds)

    def updateCredentials(self, threemaId, username="", password=""):
        return self.credentialsClient.update(threemaId, username, password)

    def getCredentialsDetails(self, threemaId):
        return self.credentialsClient.getDetails(threemaId)

    def deleteCredentials(self, threemaId):
        return self.credentialsClient.deleteCredentials(threemaId)
