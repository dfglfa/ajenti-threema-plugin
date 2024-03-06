import logging
from aj.api.endpoint import endpoint
from aj.api.http import HttpPlugin, delete, get, post, put
from jadi import component
from aj.auth import authorize

from threema.utils import CLASS_TO_LEVEL

from threema.threemaapi import ThreemaAdminClient


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.client = ThreemaAdminClient()

    @get(r'/api/threema_connector/credentials')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_get_all_credentials(self, http_context):
        pageSize = http_context.query.get("pageSize", 50)
        page = http_context.query.get("page", 0)
        return [c.toJsonDict() for c in self.client.getAllCredentials(
            page=page, pageSize=pageSize)]

    @post(r'/api/threema_connector/credentials/check')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_check_credentials(self, http_context):
        body = http_context.json_body()
        idsToCheck = body.get("idsToCheck")

        if idsToCheck:
            return self.client.checkConsistencyForStudentIds(idsToCheck)
        else:
            return self.client.checkConsistencyForAllStudents()

    @post(r'/api/threema_connector/credentials/update')
    @authorize('lm:threema:change')
    @endpoint(api=True)
    def handle_api_post_credentials_update(self, http_context):
        body = http_context.json_body()

        threemaId, changedName, changedPassword = body.get(
            "threemaId"), body.get("changedName"), body.get("changedPassword")

        self.client.updateCredentials(
            threemaId=threemaId, username=changedName, password=changedPassword)

        return "ok"

    @put(r'/api/threema_connector/credentials')
    @authorize('lm:threema:change')
    @endpoint(api=True)
    def handle_api_create_credentials(self, http_context):
        body = http_context.json_body()
        username = body.get("username")

        return self.client.createCredentials(username, password="")

    @delete(r'/api/threema_connector/credentials/(?P<threemaId>.+)')
    @authorize('lm:threema:change')
    @endpoint(api=True)
    def handle_api_delete_credentials(self, http_context, threemaId=""):
        return self.client.deleteCredentials(threemaId)

    @get(r'/api/threema_connector/credentials_with_passwords')
    @authorize('lm:threema:passwords')
    @endpoint(api=True)
    def handle_api_get_all_credentials_with_passwords(self, http_context):
        classname = http_context.query.get("classname", "")
        if classname not in CLASS_TO_LEVEL:
            logging.error(
                "You must specify a class name, unfiltered is not allowed")
            return []
        return [c.toJsonDict(includePasswords=True) for c in self.client.getAllCredentials(classname=classname)]

    @get(r'/api/threema_connector/groups')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_get_all_groups(self, http_context):
        return self.client.getGroups()

    @post(r'/api/threema_connector/groups')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_create_group(self, http_context):
        body = http_context.json_body()
        return self.client.createGroup(name=body.get("name"), members=body.get("members", []))

    @get(r'/api/threema_connector/group_details')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_get_group_details(self, http_context):
        groupId = http_context.query.get("groupId")
        return self.client.getGroupDetails(groupId=groupId)

    @get(r'/api/threema_connector/group_members')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_get_group_members(self, http_context):
        groupId = http_context.query.get("groupId")
        return self.client.getGroupMembers(groupId=groupId)

    @post(r'/api/threema_connector/group_members')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_add_group_members(self, http_context):
        body = http_context.json_body()
        return self.client.addGroupMembers(groupId=body.get("groupId"), members=body.get("members"))

    @post(r'/api/threema_connector/group_members/csv')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_search_users_by_csv(self, http_context):
        body = http_context.json_body()
        newMembers, notFound = self.client.getUsersByCSV(
            csvData=body.get("data"))
        return {"added": newMembers, "notFound": [c.toJsonDict() for c in notFound]}

    @post(r'/api/threema_connector/remove_group_members')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_remove_group_members(self, http_context):
        body = http_context.json_body()
        return self.client.removeGroupMembers(groupId=body.get("groupId"), memberIds=body.get("memberIds"))

    @get(r'/api/threema_connector/users')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_get_users(self, http_context):
        return self.client.getAllUsers()

    @delete(r'/api/threema_connector/users/(?P<threemaId>.+)')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_delete_user(self, http_context, threemaId=""):
        if threemaId:
            self.client.deleteUser(threemaId)

    @get(r'/api/threema_connector/contacts')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_get_contacts(self, http_context):
        return self.client.getContacts()

    @post(r'/api/threema_connector/contacts')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_create_contact(self, http_context):
        body = http_context.json_body()
        threemaId = body.get("threemaId")
        firstName = body.get("firstName")
        lastName = body.get("lastName")
        return self.client.createContact(threemaId, firstName, lastName)

    @delete(r'/api/threema_connector/contacts/delete')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_delete_contacts(self, http_context):
        body = http_context.json_body()
        threemaId = body.get("threemaId")
        return self.client.deleteContact(threemaId)

    @get(r'/api/threema_connector/normalizations')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_get_normalizations(self, http_context):
        return self.client.findNormalizations()

    @post(r'/api/threema_connector/normalize')
    @authorize('lm:threema:list')
    @endpoint(api=True)
    def handle_api_apply_change(self, http_context):
        body = http_context.json_body()
        threemaId = body.get("threemaId")
        firstname = body.get("firstName")
        lastname = body.get("lastName")
        enabled = body.get("enabled")
        return self.client.applyContactChange(threemaId, firstname, lastname, enabled)
