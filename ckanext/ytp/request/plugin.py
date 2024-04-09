from ckan import plugins
from ckan.plugins import implements, toolkit #type:ignore
from ckan.lib.plugins import DefaultTranslation #type:ignore

from ckanext.ytp.request.logic.action import get, create, update, delete
from ckanext.ytp.request.logic.auth import get as auth_get, create as auth_create, update as auth_update, delete as auth_delete
from ckanext.ytp.request.command.cli import get_commands
from ckanext.ytp.request import blueprint
from ckanext.ytp.request.logic.helper import helper

import logging
log = logging.getLogger(__name__)


class YtpRequestPlugin(plugins.SingletonPlugin, DefaultTranslation):
    implements(plugins.IConfigurer, inherit=True)
    implements(plugins.IActions, inherit=True)
    implements(plugins.IAuthFunctions, inherit=True)
    implements(plugins.IClick)
    implements(plugins.IBlueprint)
    implements(plugins.ITemplateHelpers)
    implements(plugins.ITranslation)

    # IConfigurer #
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('public/javascript/', 'request_js')

    # IActions
    def get_actions(self):
        return {
            "member_request_create": create.member_request_create,
            "member_request_cancel": delete.member_request_cancel,
            "member_request_reject": update.member_request_reject,
            "member_request_approve": update.member_request_approve,
            "member_request_membership_cancel": delete.member_request_membership_cancel,
            "member_requests_list": get.member_requests_list,
            "member_requests_mylist": get.member_requests_mylist,
            "get_available_roles": get.get_available_roles,
            "member_request_show": get.member_request
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            "member_request_create": auth_create.member_request_create,
            "member_request_cancel": auth_delete.member_request_cancel,
            "member_request_reject": auth_update.member_request_reject,
            "member_request_approve": auth_update.member_request_approve,
            "member_request_membership_cancel": auth_delete.member_request_membership_cancel,
            "member_requests_list": auth_get.member_requests_list,
            "member_requests_mylist": auth_get.member_requests_mylist,
            "member_request_show": auth_get.member_request
        }
    
    #Bleuprint
    def get_blueprint(self):
        return [blueprint.ytp_request]
    
    #IHelpers
    def get_helpers(self):
        return {
            "get_user_member": helper.get_user_member,
            "get_organization_admins": helper.get_organization_admins,
            "get_ckan_admins": helper.get_ckan_admins,
            "get_default_locale": helper.get_default_locale,
            "get_safe_locale": helper.get_safe_locale
        }
    
    #IClick
    def get_commands(self):
        return get_commands()