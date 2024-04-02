from ckan.plugins import toolkit #type:ignore

import logging
log = logging.getLogger(__name__)


def member_request_create(context, data_dict):
    """
    Only allow to logged in users
    """
    if not toolkit.current_user:
        return {'success': False, 'msg': toolkit._(u'User is not logged in')}

    organization_id = None if not data_dict else data_dict.get(
        'organization_id', None)
    if organization_id:
        member = toolkit.h.get_user_member(organization_id)
        if member:
            return {'success': False, 'msg': toolkit._(u'The user has already a pending request or an active membership')}
    return {'success': True}
