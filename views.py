import json
from jadi import component

from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

from .threema.threemaapi import ThreemaAdminClient


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.client = ThreemaAdminClient()

    @get(r'/api/threema_connector')
    @endpoint(api=True)
    def handle_api_get_example_threema_connector(self, http_context):
        text = "This content was generated through a GET call to Python !"
        return text

    @get(r'/api/threema_connector/credentials')
    @endpoint(api=True)
    def handle_api_get_all_credentials(self, http_context):
        pageSize = http_context.query.get("pageSize", 50)
        page = http_context.query.get("page", 0)
        return [c.toJsonDict() for c in self.client.getAllCredentials(
            page=page, pageSize=pageSize)]

    @get(r'/api/threema_connector/credentials/check')
    @endpoint(api=True)
    def handle_api_check_credentials(self, http_context):
        return self.client.checkConsistencyForAllStudents()

    @post(r'/api/threema_connector')
    @endpoint(api=True)
    def handle_api_post_example_threema_connector(self, http_context):
        data = http_context.json_body()['my_var']
        text = "This content in the module %s was generated through a POST call to Python !" % data
        return text
