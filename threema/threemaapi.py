
import logging


from threema.contactsclient import ContactsClient
from threema.normalizationClient import NormalizationClient
from threema.config_loader import getThreemaApiKey, getThreemaBroadcastApiKey, getThreemaBroadcastId
from threema.credentialsclient import CredentialsClient
from threema.userclient import UserClient
from threema.groupclient import GroupClient
from threema.datamodel import Contact
from threema.entuserdataprovider import ENTUserDataProvider
from threema.utils import readRecordsFromCSV

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

    def __init__(self):
        self.userClient = UserClient(
            DEFAULT_USERS_BASE_URL, authHeader={"X-Api-Key": API_KEY})
        self.credentialsClient = CredentialsClient(
            DEFAULT_USERS_BASE_URL, authHeader={"X-Api-Key": API_KEY})
        self.contactsClient = ContactsClient(
            DEFAULT_USERS_BASE_URL, authHeader={"X-Api-Key": API_KEY})
        self.groupsClient = GroupClient(BROADCAST_ID,
                                        DEFAULT_BROADCAST_BASE_URL, authHeader={"X-Api-Key": BROADCAST_API_KEY})
        self.normalizationClient = NormalizationClient(
            self.credentialsClient, self.userClient, self.contactsClient, ENTUserDataProvider())

    def getAllUsers(self, **params):
        return self.userClient.getAll(**params)

    def deleteUser(self, threemaId):
        return self.userClient.deleteUser(threemaId)

    def getAllCredentials(self, **params):
        return self.credentialsClient.getAll(**params)

    def createCredentials(self, username, password):
        return self.credentialsClient.create(username, password)

    def checkCredentialsNamingScheme(self):
        return self.credentialsClient.checkNamingScheme()

    def correctCredentialsNamingScheme(self):
        return self.credentialsClient.correctNamingScheme()

    def checkConsistencyForAllStudents(self):
        return self.credentialsClient.matchAgainstMasterUserData()

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

    def getGroupDetails(self, groupId):
        return self.groupsClient.getGroupDetails(groupId)

    def getGroupMembers(self, groupId) -> list[Contact]:
        members = self.groupsClient.getGroupMembers(groupId)
        return self.contactsClient.getContactsForUserIds([m["id"] for m in members])

    def createGroup(self, name, members):
        return self.groupsClient.createGroup(name, members)

    def addGroupMembers(self, groupId, members):
        return self.groupsClient.addGroupMembers(groupId, members)

    def removeGroupMembers(self, groupId, memberIds):
        return self.groupsClient.removeGroupMembers(groupId, memberIds)

    def getUsersByCSV(self, csvData):
        records = readRecordsFromCSV(csvData)
        creds = self.credentialsClient.findMatchesForRecords(records)
        foundIds, notFoundCredentials = self.userClient.searchUsersByCredentials(
            creds)

        foundContacts = self.contactsClient.getContactsForUserIds(foundIds)

        return foundContacts, notFoundCredentials

    def getContacts(self):
        return self.contactsClient.getAll()

    def createContact(self, threemaId, firstName, lastName):
        return self.contactsClient.createContact(threemaId, firstName, lastName)

    def deleteContact(self, threemaId):
        self.contactsClient.deleteContact(threemaId)

    def findNormalizations(self):
        return self.normalizationClient.findNormalizations()

    def applyContactChange(self, threemaId, firstname, lastname, enabled):
        return self.contactsClient.updateContact(threemaId, firstname, lastname, enabled)
