from ckan.plugins import toolkit #type:ignore
#FIXME dont use C or g
from ckan.common import c

import logging
log = logging.getLogger(__name__)


def _member_common_access_check(context, data_dict, status):

    if not c.userobj:
        return {'success': False}

    organization_id = data_dict.get("organization_id")
    if not organization_id:
        return {'success': False}

    member = toolkit.h.get_user_member(organization_id, status)
    
    if not member:
        return {'success': False}
    
    #FIXME dont use C or G
    if member.table_name == 'user' and member.table_id == c.userobj.id and member.state == status:
        return {'success': True}
    return {'success': False}


def member_request_membership_cancel(context, data_dict):
    return _member_common_access_check(context, data_dict, 'active')


def member_request_cancel(context, data_dict):
    return _member_common_access_check(context, data_dict, 'pending')
