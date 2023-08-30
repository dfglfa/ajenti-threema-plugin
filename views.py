import logging
from aj.api.endpoint import endpoint
from aj.api.http import HttpPlugin, delete, get, post, put
from jadi import component
from aj.auth import authorize

from .threema.utils import CLASS_TO_LEVEL

from .threema.threemaapi import ThreemaAdminClient


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
