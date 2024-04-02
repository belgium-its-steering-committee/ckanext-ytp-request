import logging
from ckan import model, authz
from ckan.common import c
from ckan.plugins import toolkit #type:ignore

log = logging.getLogger(__name__)


def member_request(context, data_dict):
    """
    Only allowed to sysadmins or organization admins
    :param context: context object
    :param data_dict: data dictionary
    :type context: dict
    :type data_dict: dict
    """
    #FIXME Dont use C or G
    if not c.userobj:
        return {'success': False}

    #FIXME Dont use C or G
    if authz.is_sysadmin(c.user):
        return {'success': True}

    membership = model.Member.get(data_dict.get("mrequest_id"))
    if not membership:
        return {'success': False}

    if membership.table_name != 'user':
        return {'success': False}

    #FIXME Dont use C or g
    query = model.Session.query(model.Member)\
        .filter(model.Member.state == 'active')\
        .filter(model.Member.table_name == 'user')\
        .filter(model.Member.capacity == 'admin')\
        .filter(model.Member.table_id == c.userobj.id)\
        .filter(model.Member.group_id == membership.group_id)
    return {'success': query.count() > 0}


def member_requests_mylist(context, data_dict):
    """
    Show request access check
    :param context: context object
    :param data_dict: data dictionary
    :type context: dict
    :type data_dict: dict
    """
    # TODO: Sysadmins dont have this functionality since it is pointless. Make
    # it at the logical level
    # tip:: toolkit.current_user[sysadmin]
    return _only_registered_user(context, data_dict)


def member_requests_list(context, data_dict):
    """
    Show request access check
    :param context: context object
    :param data_dict: data dictionary
    :type context: dict
    :type data_dict: dict
    """
    return _only_registered_user(context, data_dict)


def _only_registered_user(context, data_dict):
    if not toolkit.current_user:
        return {'success': False, 'msg': toolkit._(u'User is not logged in')}
    return {'success': True}
