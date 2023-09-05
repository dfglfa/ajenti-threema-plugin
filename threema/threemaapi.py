
import logging


from .config_loader import getThreemaApiKey, getThreemaBroadcastApiKey, getThreemaBroadcastId
from .credentialsclient import CredentialsClient
from .userclient import UserClient
from .groupclient import GroupClient

API_KEY = getThreemaApiKey()
if not API_KEY:
    logging.error("*" * 50)
    logging.error(
        "WARNING: API_KEY not readable from standard location /etc/linuxmuster/webui/threema.yml")
    logging.error("Threema access will NOT work.")
    logging.error("*" * 50)

BROADCAST_ID = getThreemaBroadcastId()
if not BROADCAST_ID:
    logging.error("Threema broadcast ID not found")

BROADCAST_API_KEY = getThreemaBroadcastApiKey()
if not BROADCAST_ID:
    logging.warn("Threema broadcast API key not found")

DEFAULT_USERS_BASE_URL = "https://work.threema.ch/api/v1"
DEFAULT_BROADCAST_BASE_URL = "https://broadcast.threema.ch/api/v1"


class ThreemaAdminClient:

    def __init__(self, baseUrl=DEFAULT_USERS_BASE_URL):
        self.baseUrl = baseUrl
        self.userClient = UserClient(
            baseUrl, authHeader={"X-Api-Key": API_KEY})
        self.credentialsClient = CredentialsClient(
            baseUrl, authHeader={"X-Api-Key": API_KEY})
        self.groupsClient = GroupClient(BROADCAST_ID,
                                        DEFAULT_BROADCAST_BASE_URL, authHeader={"X-Api-Key": BROADCAST_API_KEY})

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

    def getGroups(self):
        return self.groupsClient.getAllGroups()
