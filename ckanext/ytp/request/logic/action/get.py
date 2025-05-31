from ckan import model
from ckan.plugins import toolkit #type:ignore
from ckan.lib.dictization import model_dictize #type:ignore
from ckan.logic import side_effect_free #type: ignore
from ckanext.ytp.request.model import MemberRequest

#use toolkit
#from ckanext.ytp.request.helper import get_organization_admins
#from ckan.common import _


#use toolkit
#import ckan.authz as authz

import logging
log = logging.getLogger(__name__)


def member_request(context, data_dict):
    """
    :param context: context object
    :param data_dict: data dictionary
    :type context: dict
    :type data_dict: dict
    """
    toolkit.check_access('member_request_show', context, data_dict)
    mrequest_id = data_dict.get('mrequest_id', None)

    membership = model.Session.query(model.Member).get(mrequest_id)
    if not membership or membership.state != 'pending':
        raise toolkit.ObjectNotFound(404, detail=toolkit.u(u"Member request not found"))

    # Return most current instance from memberrequest table
    member_request_obj = model.Session.query(MemberRequest)\
        .filter( MemberRequest.membership_id == mrequest_id)\
        .order_by(MemberRequest.request_date.desc()).limit(1).first()
    
    if not member_request_obj or member_request_obj.status != 'pending':
        raise toolkit.ObjectNotFound (404,toolkit._(u"Member request associated with membership not found"))

    member_dict = {
        'id': mrequest_id,
        'organization_name': membership.group.name,
        'group_id': membership.group_id,
        'role': member_request_obj.role,
        'state': 'pending',
        'request_date': member_request_obj.request_date.strftime("%d - %b - %Y"),
        'user_id': membership.table_id
    }
    return member_dict


def member_requests_mylist(context, data_dict):
    """
    Users wil see a list of her member requests
    :param context: context object
    :param data_dict: data dictionary
    :type context: dict
    :type data_dict: dict
    """
    toolkit.check_access('member_requests_mylist', context, data_dict)
    user = toolkit.current_user
    if user.sysadmin:
        raise toolkit.ValidationError({}, {_("Role"): toolkit._("As a sysadmin, you already have access to all organizations")})

    user_object = model.User.get(user.id)
    # Return current state for memberships for all organizations for the user (last modified date)
    membership_requests = model.Session.query(model.Member)\
        .filter(model.Member.table_id == user_object.id).all()
    
    return _membeship_request_list_dictize(membership_requests, context)


def member_requests_list(context, data_dict):
    """
    Organization admins/editors will see a list of member requests to be approved.
    :param context: context object
    :param data_dict: data dictionary
    :type context: dict
    :type data_dict: dict
    """
    toolkit.check_access('member_requests_list', context, data_dict)
    
    user = context.get('user', None)
    user = toolkit.current_user
    user_object = model.User.get(user.id)
    is_sysadmin = user.sysadmin

    # ALL members with pending state only
    query = model.Session.query(model.Member)\
        .filter(model.Member.table_name == 'user')\
        .filter(model.Member.state == 'pending')

    if not is_sysadmin:
        admin_in_groups = model.Session.query(model.Member)\
            .filter(model.Member.state == 'active')\
            .filter(model.Member.table_name == 'user') \
            .filter(model.Member.capacity == 'admin')\
            .filter(model.Member.table_id == user_object.id)

        if admin_in_groups.count() <= 0:
            return []
        # members requests for this organization
        admin_group_ids = [admin.group_id for admin in admin_in_groups]
        query = query\
            .filter(model.Member.group_id.in_(admin_group_ids))
    
    group = data_dict.get('group', None)
    if group:
        group_object = model.Group.get(group)
        if group_object:
            query = query.filter(model.Member.group_id == group_object.id)

    members = query.all()
    return _member_list_dictize(members, context)

#TODO all roles just be available
@side_effect_free
def get_available_roles(context, data_dict=None):
    roles = toolkit.get_action("member_roles_list")(context, {})
    # Remove member role from the list - if needed
    # roles = [role for role in roles if role['value'] != 'member']
    # If organization has no associated admin, then role editor is not
    # available
    organization_id = toolkit.get_or_bust(data_dict, 'organization_id')
    print("\t\n Organization_id ::", organization_id, "\n")
    if organization_id:
        if toolkit.h.get_organization_admins(organization_id):
            roles = [role for role in roles if role['value'] != 'editor']
            print("\t\n ROLES_03::", roles, "\n")
        return roles
    else:
        return None


def _membeship_request_list_dictize(obj_list, context):
    """Helper to convert member requests list to dictionary """
    result_list = []
    for obj in obj_list:
        member_dict = {}
        organization = model.Session.query(model.Group).get(obj.group_id)
        # Fetch the newest member_request associated to this membership (sort
        # by last modified field)
        member_request_obj = model.Session.query(MemberRequest)\
            .filter(MemberRequest.membership_id == obj.id)\
            .order_by(MemberRequest.request_date.desc())\
            .limit(1)\
            .first()
        # Filter out those with cancel state as there is no need to show them to the end user
        # Show however those with 'rejected' state as user may want to know about them
        # HUOM! If a user creates itself a organization has already a
        # membership but doesnt have a member_request
        member_dict['organization_name'] = organization.name
        member_dict['organization_id'] = obj.group_id
        member_dict['role'] = 'admin'
        member_dict['state'] = 'active'
        # We use the member_request state since there is also rejected and
        # cancel
        if member_request_obj is not None and member_request_obj.status != 'cancel':
            member_dict['state'] = member_request_obj.status
            member_dict['role'] = member_request_obj.role
            member_dict['request_date'] = member_request_obj.request_date.strftime(
                "%d - %b - %Y")
            if member_request_obj.handling_date:
                member_dict['handling_date'] = member_request_obj.handling_date.strftime(
                    "%d - %b - %Y")
                member_dict['handled_by'] = member_request_obj.handled_by
        if member_request_obj is None or member_request_obj.status != 'cancel':
            result_list.append(member_dict)
    return result_list


def _member_list_dictize(obj_list, context, sort_key=lambda x: x['group_id'], reverse=False):
    """ Helper to convert member list to dictionary """
    result_list = []
    for obj in obj_list:
        member_dict = model_dictize.member_dictize(obj, context)
        user = model.Session.query(model.User).get(obj.table_id)

        member_dict['group_name'] = obj.group.name if obj.group is not None else None
        member_dict['role'] = obj.capacity
        # Member request must always exist since state is pending. Fetch just
        # the latest
        member_request_obj = model.Session.query(MemberRequest)\
            .filter(MemberRequest.membership_id == obj.id)\
            .filter(MemberRequest.status == 'pending')\
            .order_by(MemberRequest.request_date.desc())\
            .limit(1)\
            .first()
        # This should never happen but..
        my_date = ""
        if member_request_obj is not None:
            my_date = member_request_obj.request_date.strftime("%d - %b - %Y")

        member_dict['request_date'] = my_date
        member_dict['mid'] = obj.id
        member_dict['user_name'] = user.name
        
        result_list.append(member_dict)
    return sorted(result_list, key=sort_key, reverse=reverse)
