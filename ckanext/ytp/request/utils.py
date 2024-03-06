from ckan import logic, model
from ckan.lib import helpers
from ckan.plugins import toolkit
from ckan.common import c, _
import ckan.lib.navl.dictization_functions as dict_fns
import logging

log = logging.getLogger(__name__)


not_auth_message = _('Unauthorized')
request_not_found_message = _('Request not found')

def _list_organizations(context, errors=None, error_summary=None):
    data_dict = {}
    context = {}
    data_dict['limit']= 1000
    data_dict['all_fields'] = True
    data_dict['include_datset_count'] = False
    data_dict['include_extras'] = False
    data_dict['include_tags']= False
    data_dict['include_users'] = False
    # TODO: Filter our organizations where the user is already a member or
    # Set in config: ckan.group_and_organization_list_max to...
    # has a pending request
    return toolkit.get_action('organization_list')(context, data_dict)

def new(organization_id, errors=None, error_summary=None):
    #TODO WHERE DOES SAVE COMMES FROM (SAVE FROM URL?)
    context = {'user': c.user or c.author,
                'save': 'save' in toolkit.request.params}

    try:
        toolkit.check_access('member_request_create', context)
    except toolkit.NotAuthorized:
        toolkit.abort(401, errors.not_auth_message)

    organizations = _list_organizations(context)

    if context.get('save') and not errors:
        return _save_new(context)

    # FIXME: Don't send as request parameter selected organization. kinda
    # weird
    selected_organization = str(organization_id)
    extra_vars = {'selected_organization': selected_organization, 'organizations': organizations,
                    'errors': errors or {}, 'error_summary': error_summary or {}}
    c.roles = _get_available_roles(context, selected_organization)
    c.user_role = 'admin'
    print("ORGANIZATIONS:: ")
    for org in organizations:
        print("\t", org['id'])
    print("\n\t SELECTED ORGANIZATION:: ", organization_id)
    c.form = toolkit.render("request/new_request_form.html", extra_vars=extra_vars)
    return toolkit.render("request/new.html")

def _save_new(context):
    try:
        data_dict = logic.clean_dict(dict_fns.unflatten(
            logic.tuplize_dict(logic.parse_params(toolkit.request.params))))
        data_dict['group'] = data_dict['organization']
        # TODO: Do we need info message at the UI level when e-mail could
        # not be sent?
        member = toolkit.get_action(
            'member_request_create')(context, data_dict)
        helpers.redirect_to('organizations_index',
                            id="newrequest", membership_id=member['id'])
    except dict_fns.DataError:
        toolkit.abort(400, _(u'Integrity Error'))
    except logic.NotFound:
        toolkit.abort(404, _('Item not found'))
    except logic.NotAuthorized:
        toolkit.abort(405, self.not_auth_message)
    except logic.ValidationError as e:
        errors = e.error_dict if e.error_dict else True
        error_summary = e.error_summary
        return self.new(errors, error_summary)

def show(self, mrequest_id):
    """" Shows a single member request. To be used by admins in case they want to modify granted role or accept via e-mail """
    context = {'user': c.user or c.author}
    try:
        membershipdto = toolkit.get_action('member_request_show')(
            context, {'mrequest_id': mrequest_id})
        member_user = model.Session.query(
            model.User).get(membershipdto['user_id'])
        context = {'user': member_user.name}
        roles = self._get_available_roles(
            context, membershipdto['organization_name'])
        extra_vars = {"membership": membershipdto,
                        "member_user": member_user, "roles": roles}
        return toolkit.render('request/show.html', extra_vars=extra_vars)
    except logic.NotFound:
        toolkit.abort(404, self.request_not_found_message)
    except logic.NotAuthorized:
        toolkit.abort(401, self.not_auth_message)

def mylist(self):
    """" Lists own members requests (possibility to cancel and view current status)"""
    context = {'user': c.user or c.author}
    id = toolkit.request.params.get('id', None)
    try:
        my_requests = toolkit.get_action(
            'member_requests_mylist')(context, {})
        message = None
        if id:
            message = _("Member request processed successfully")
        extra_vars = {'my_requests': my_requests, 'message': message}
        return toolkit.render('request/mylist.html', extra_vars=extra_vars)
    except logic.NotAuthorized:
        toolkit.abort(401, self.not_auth_message)

def list(self):
    """ Lists member requests to be approved by admins"""
    context = {'user': c.user or c.author}
    id = toolkit.request.params.get('id', None)
    selected_organization = toolkit.request.params.get('selected_organization', None)
    if selected_organization:
        organization = toolkit.get_action('organization_show')(context, {'id': selected_organization})
        member_requests = toolkit.get_action('member_requests_list')(context, {'group': selected_organization})
    else:
        organization = None
        member_requests = None
    try:
        message = None
        if id:
            message = _("Member request processed successfully")
        log.debug("%s", message)
        extra_vars = {
            'member_requests': member_requests, 'message': message, 'group_dict': organization,
            'group_type': 'organization'}
        return toolkit.render('request/list.html', extra_vars=extra_vars)
    except logic.NotAuthorized:
        toolkit.abort(401, self.not_auth_message)

def cancel(organization_id, errors=None, error_summary=None):
    """ Logged in user can cancel pending requests not approved yet by admins/editors"""
    context = {'user': c.user or c.author}
    #organization_id = toolkit.request.params.get('organization_id', None)
    try:
        toolkit.get_action('member_request_cancel')(
            context, {"organization_id": organization_id})
        id = 'cancel'
        helpers.redirect_to('member_requests_mylist', id=id)
    except logic.NotAuthorized:
        toolkit.abort(401, self.not_auth_message)
    except logic.NotFound:
        toolkit.abort(404, self.request_not_found_message)

def reject(self, mrequest_id):
    """ Controller to reject member request (only admins or group editors can do that """
    return self._processbyadmin(mrequest_id, False)

def approve(self, mrequest_id):
    """ Controller to approve member request (only admins or group editors can do that) """
    return self._processbyadmin(mrequest_id, True)

def membership_cancel(organization_id, errors=None, error_summary=None):
    """ Logged in user can cancel already approved/existing memberships """
    context = {'user': c.user or c.author}
    try:
        toolkit.get_action('member_request_membership_cancel')(
            context, {"organization_id": organization_id})
        id = 'cancel'
        helpers.redirect_to('member_requests_mylist', id=id)
    except logic.NotAuthorized:
        toolkit.abort(401, self.not_auth_message)
    except logic.NotFound:
        toolkit.abort(404, self.request_not_found_message)

def _get_available_roles(context, organization_id):
    data_dict = {'organization_id': organization_id}
    return toolkit.get_action('get_available_roles')(context, data_dict)

def _processbyadmin(self, mrequest_id, approve):
    context = {'user': c.user or c.author}
    role = toolkit.request.params.get('role', None)
    data_dict = {"mrequest_id": mrequest_id, 'role': role}
    try:
        if approve:
            toolkit.get_action('member_request_approve')(
                context, data_dict)
            id = 'approved'
        else:
            toolkit.get_action('member_request_reject')(context, data_dict)
            id = 'rejected'
        helpers.redirect_to("member_requests_list", id=id)
    except logic.NotAuthorized:
        toolkit.abort(401, self.not_auth_message)
    except logic.NotFound:
        toolkit.abort(404, self.request_not_found_message)
    except logic.ValidationError as e:
        toolkit.abort(400, str(e))
