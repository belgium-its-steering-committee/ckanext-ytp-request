from ckan import logic, model
from ckan.plugins import toolkit #type:ignore
#FIXME Avoid use c or g
from ckan.common import c #type:ignore

import logging
log = logging.getLogger(__name__)


not_auth_message = toolkit._(u'Unauthorized')
request_not_found_message = toolkit._(u'Membership Request has already been approved, or does not exist.')
not_found_message= toolkit._(u'Item not found')


def new(organization_id):
    #FIXME: Using c
    context = {'user': c.user or c.author,
               'save': toolkit.request.form.get('form_save_new_request'),
                }
    
    data_dict= {'organization_id': organization_id,
                'role': toolkit.request.form.get('role')
                }
    try:
        toolkit.check_access('member_request_create', context)
    except toolkit.NotAuthorized:
        toolkit.abort(401, detail=not_auth_message)

    organizations = _list_organizations()

    if context.get('save'):
        return _save_new(context, data_dict)

    selected_organization = str(organization_id)
    
    extra_vars = {'selected_organization': selected_organization, 'organizations': organizations}
    
    #FIXME: Don't use C (or g)
    c.roles = _get_available_roles(context, selected_organization)
    c.user_role = 'admin'
    c.form = toolkit.render("request/new_request_form.html", extra_vars=extra_vars)
    
    return toolkit.render("request/new.html")
        
def show(mrequest_id):
    """" Shows a single member request. To be used by admins in case they want to modify granted role or accept via e-mail """
    #FIXME: dont use c or g
    context = {'user': c.user or c.author}
    try:
        membershipdto = toolkit.get_action('member_request_show')(
            context, {'mrequest_id': mrequest_id})
        
        #session 
        member_user = model.Session.query(
            model.User).get(membershipdto['user_id'])
        context = {'user': member_user.name}
        
        #Backup roles::
        #roles=['admin','editor']
        roles = _get_available_roles(
            context, membershipdto['organization_name'])
        
        extra_vars = {"membership": membershipdto,
                        "member_user": member_user, "roles": roles}
        
        return toolkit.render('request/show.html', extra_vars=extra_vars)
    
    except toolkit.ObjectNotFound:
        toolkit.abort(404, detail=request_not_found_message)
    except logic.NotAuthorized:
        toolkit.abort(401, detail=not_auth_message)

def mylist(id):
    """" Lists own members requests (possibility to cancel and view current status)"""
    
    #FIXME: dont use c or g
    context = {'user': c.user or c.author}
    id = (id, None)
    message = None
    
    try:
        my_requests = toolkit.get_action('member_requests_mylist')(
            context, {})        
        if id:
            message = toolkit._("Member request processed successfully")
        extra_vars = {'my_requests': my_requests, 'message': message}
        
        return toolkit.render('request/mylist.html', extra_vars=extra_vars)
    
    except toolkit.NotAuthorized:
        toolkit.abort(401, detail=not_auth_message)

def list():
    """ Lists member requests to be approved by admins"""
    
    #FIXME dont use C or G
    context = {'user': c.user or c.author}
    organization = None
    member_requests = None
    message = None
    
    #get params from url request
    id = toolkit.request.args.get('id', None)
    selected_organization = toolkit.request.args.get('selected_organization', None)
    
    if selected_organization:
        organization = toolkit.get_action('organization_show')(context, {'id': selected_organization})
        member_requests = toolkit.get_action('member_requests_list')(context, {'group': selected_organization})
    
    try:
        if id:
            message = toolkit._("Member request processed successfully")

        extra_vars = {
            'member_requests': member_requests, 'message': message, 'group_dict': organization,
            'group_type': 'organization'}
        
        return toolkit.render('request/list.html', extra_vars=extra_vars)
    
    except toolkit.NotAuthorized:
        toolkit.abort(401, detail=not_auth_message)

def cancel(organization_id):
    """ Logged in user can cancel pending requests not approved yet by admins/editors"""
    
    #FIXME dont use c or g
    context = {'user': c.user or c.author}
    
    try:
        toolkit.get_action('member_request_cancel')(
            context, {"organization_id": organization_id})
        id = 'cancel'
        return toolkit.redirect_to('ytp_request.mylist', id=id)
    
    except toolkit.NotAuthorized:
        toolkit.abort(401, detail=not_auth_message)
    except toolkit.ObjectNotFound:
        toolkit.abort(404, detail=request_not_found_message)

def reject(mrequest_id):
    """ Controller to reject member request (only admins or group editors can do that """
    return _processbyadmin(mrequest_id, False)

def approve(mrequest_id):
    """ Controller to approve member request (only admins or group editors can do that) """
    return _processbyadmin(mrequest_id, True)

def membership_cancel(organization_id):
    """ Logged in user can cancel already approved/existing memberships """
    #FIXME dont use c or g
    context = {'user': c.user or c.author}
    
    try:
        toolkit.get_action('member_request_membership_cancel')(
            context, {"organization_id": organization_id})
        id = 'cancel'
        return toolkit.redirect_to('ytp_request.mylist', id=id)
    
    except logic.NotAuthorized:
        toolkit.abort(401, detail=not_auth_message)
    
    except logic.NotFound:
        toolkit.abort(404, detail=request_not_found_message)

def _save_new(context, data_dict):
    try:
        data_dict['group'] = data_dict['organization_id']
        #create member
        toolkit.get_action("member_request_create")(context, data_dict)
        #return to organization
        return toolkit.h.redirect_to('organization.read',id=data_dict.get('organization_id'))
    
    #TODO dict_fns.dataError depriciated
    #except dict_fns.DataError:
        #toolkit.abort(400, message= _(u'Integrity Error'))
    except toolkit.ObjectNotFound:
        toolkit.abort(404, detail=not_found_message)
    except toolkit.NotAuthorized:
        toolkit.abort(401, detail = not_auth_message)
    except toolkit.ValidationError as e:
        #FIXME e-error handling
        toolkit.abort(400, detail = str(e))

def _list_organizations():
    context = {}
    data_dict = {}
    data_dict['all_fields'] = True
    data_dict['include_datset_count'] = False
    data_dict['include_extras'] = False
    data_dict['include_tags']= False
    data_dict['include_users'] = False
    #TODO: Filter organization_list
    """
    Filter out organizations where the user is already a member or has a pending request
    """
    try:
        return toolkit.get_action('organization_list')(context, data_dict)
    except toolkit.ObjectNotFound:
        toolkit.abort(404, detail="No organization are found")

def _get_available_roles(context, organization_id):
    data_dict = {'organization_id': organization_id}
    return toolkit.get_action('get_available_roles')(context, data_dict)

def _processbyadmin(mrequest_id, approve):
    
    #FIXME dont use c or g
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
        return toolkit.redirect_to("ytp_request.list", id=id)
    
    except toolkit.NotAuthorized:
        toolkit.abort(401, detail=not_auth_message)
    except toolkit.ObjectNotFound:
        toolkit.abort(404, detail=request_not_found_message)
    except toolkit.ValidationError as e:
        #FIXME e-error handling
        toolkit.abort(400, detail=str(e))
