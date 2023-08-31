from jadi import component

from aj.plugins.core.api.sidebar import SidebarItemProvider
from aj.auth import PermissionProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:general',
                'name': 'Threema',
                'icon': 'mobile',
                'url': '/view/threema_connector',
                'children': []
            }
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'lm:threema:list',
                'name': _('List threema users'),
                'default': False,
            },
            {
                'id': 'lm:threema:change',
                'name': _('Change threema user details, add/remove users'),
                'default': False,
            },
            {
                'id': 'lm:threema:passwords',
                'name': _('View threema passwords as cleartext'),
                'default': False,
            }
        ]
