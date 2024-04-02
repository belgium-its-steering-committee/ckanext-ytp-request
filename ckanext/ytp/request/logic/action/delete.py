from ckan import model
from ckanext.ytp.request.model import MemberRequest
from ckan.lib.dictization import model_dictize #type:ignore
from ckan.plugins import toolkit #type:ignore
#FIXME Dont use C or g
from ckan.common import c 

from sqlalchemy.sql import func #type:ignore
from sqlalchemy.sql.expression import or_ #type:ignore



import logging
log = logging.getLogger(__name__)


def member_request_cancel(context, data_dict):
    """
    Cancel own request (from logged in user). Organization_id must be provided.
    We cannot rely on membership_id since existing memberships can be created also from different ways (e.g. a user creates an organization)
    :param context: context object
    :param data_dict: data dictionary
    :type context: dict
    :type data_dict: dict
    """
    toolkit.check_access('member_request_cancel', context, data_dict)

    organization_id = data_dict.get("organization_id")
    
    query = model.Session.query(model.Member) \
        .filter(or_(model.Member.state == 'pending', model.Member.state == 'active')) \
        .filter(model.Member.table_name == 'user') \
        .filter(model.Member.table_id == c.userobj.id) \
        .filter(model.Member.group_id == organization_id)
    member = query.first()

    if not member or not member.group.is_organization:
        raise toolkit.ObjectNotFound(404, detail=toolkit._(u"No membership request found for given organization"))

    return _process_request(context, organization_id, member, 'pending')


def member_request_membership_cancel(context, data_dict):
    """
    Cancel ACTIVE organization membership (not request) from logged in user. Organization_id must be provided.
    :param context: context object
    :param data_dict: data dictionary
    :type context: dict
    :type data_dict: dict
    """
    toolkit.check_access('member_request_membership_cancel', context, data_dict)

    organization_id = data_dict.get("organization_id")
    query = model.Session.query(model.Member).filter(model.Member.state == 'active') \
        .filter(model.Member.table_name == 'user').filter(model.Member.table_id == c.userobj.id).filter(model.Member.group_id == organization_id)
    member = query.first()

    if not member or not member.group.is_organization:
        raise toolkit.ObjectNotFound(404, detail=toolkit._(u"No active memberschip found for given organization"))

    return _process_request(context, organization_id, member, 'active')


def _process_request(context, organization_id, member, status):
    """
    Cancel a member request or existing membership.
    Delete from database the member request (if existing) and set delete state in member table
    :param context: context object
    :param organization_id:
    :param member: id of the member
    :param status:
    :type context: dict
    :type organization_id:
    :type member: string
    :type status:
    """
    #user = context.get("user")
    user = toolkit.current_user
    # Logical delete on table member
    member.state = 'deleted'
    # Fetch the newest member_request associated to this membership (sort by
    # last modified field)
    member_request = model.Session.query(MemberRequest)\
        .filter( MemberRequest.membership_id == member.id)\
        .order_by(MemberRequest.request_date.desc())\
        .limit(1)\
        .first()

    # BFW: Create a new instance every time membership status is changed
    message = toolkit._(u'MemberRequest cancelled by own user')
    mrequest_date = func.now()
    locale = toolkit.h.get_safe_locale()
    if member_request is not None and member_request.status == status:
        locale = member_request.language
        mrequest_date = member_request.request_date

    #FIXME Dont use C
    member_request = MemberRequest(membership_id=member.id, role=member.capacity, status="cancel", request_date=mrequest_date,
                                   language=locale, handling_date=func.now(), handled_by=c.userobj.name, message=message)
    model.Session.add(member_request)

    member.save()
    model.repo.commit()

    return model_dictize.member_dictize(member, context)
