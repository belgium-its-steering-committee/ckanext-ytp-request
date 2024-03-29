from ckan import model, logic
from ckan.plugins import toolkit
import ckan.lib.helpers as helpers


from ckan.lib.dictization import model_dictize
from ckan.common import _
#from pylons import config
from ckanext.ytp.request.model import MemberRequest
from ckanext.ytp.request.mail import mail_new_membership_request
from ckanext.ytp.request.helper import get_safe_locale
import logging
import ckan.authz as authz


log = logging.getLogger(__name__)


def member_request_create(context, data_dict):
    """
    Create new member request. User is taken from context.
    Sysadmins should not be able to create "member" requests since they have full access to all organizations
    :param context: context object
    :param data_dict: data dictionary
    :type context: dict
    :type data_dict: dict
    """
    member = _create_member_request(context, data_dict)
    return model_dictize.member_dictize(member, context)


def _create_member_request(context, data_dict):
    """
    Helper to create member request
    :param context: context object
    :param data_dict: data dictionary
    :type context: dict
    :type data_dict: dict
    """
    role = data_dict.get('role', None)
    if not role:
        raise logic.NotFound
    
    #Get <Group> from ckan-model(db)
    group = model.Group.get(data_dict.get('group', None))
    if not group or group.type != 'organization':
        raise logic.NotFound
    
    #Get <user> from context
    user = context.get('user', None)
    if authz.is_sysadmin(user):
        raise logic.ValidationError({}, {_("Role"): _(
            "As a sysadmin, you already have access to all organizations")})
    
    #Get <user> from ckan-model(db)
    userobj = model.User.get(user)

    #If exsists, get <member> of a <group>(aka organisation)
    member = model.Session.query(model.Member).filter(model.Member.table_name == "user").filter(model.Member.table_id == userobj.id) \
        .filter(model.Member.group_id == group.id).first()
    
    # If there is a member for this organization and it is NOT deleted. Reuse
    # existing if deleted
    if member:
        if member.state == 'pending':
            message = _(
                "You already have a pending request to the organization")
        elif member.state == 'active':
            message = _("You are already part of the organization")
        # Unknown status. Should never happen..
        elif member.state != 'deleted':
            raise logic.ValidationError({"organization": _(
                "Duplicate organization request")}, {_("Organization"): ""})
    else:
        member = model.Member(table_name="user", table_id=userobj.id,
                              group_id=group.id, capacity=role, state='pending')

    
    #TODO: Is there a way to get language associated to all admins. User table there is nothing as such stored
    locale = get_safe_locale()

    member.state = 'pending'
    member.capacity = role
    if member.group is None:
        member.group = group

    #FIXME legacy? New way for testing?
    #revision = model.repo.new_revision()
    #revision.author = user
    #revision.message = u'New member request'

    model.Session.add(member)
    # We need to flush since we need membership_id (member.id) already
    model.Session.flush()

    member_request = MemberRequest(
        membership_id=member.id, role=role, status="pending", language=locale)
    model.Session.add(member_request)
    model.repo.commit()

    url = toolkit.config.get('ckan.site_url', "")
    if url:
        url = helpers.url_for('ytp_request.show',mrequest_id=member.id, _external = True )

    # Locale should be admin locale since mail is sent to admins
    if role == 'admin':
        for admin in _get_ckan_admins():
            #FIXME
            if admin.display_name == "Felten Vanballenberge SysAdmin":
                mail_new_membership_request(
                    locale, admin, group.display_name, url, userobj.display_name, userobj.email)
    else:
        for admin in _get_organization_admins(group.id):
            #FIXME
            if admin.display_name == "Felten Vanballenberge SysAdmin":
                mail_new_membership_request(
                    locale, admin, group.display_name, url, userobj.display_name, userobj.email)

    print('\n\t ReturnedMember::', member, "\n")
    return member


def _get_organization_admins(group_id):
    admins = set(model.Session.query(model.User).join(model.Member, model.User.id == model.Member.table_id).
                 filter(model.Member.table_name == "user").filter(model.Member.group_id == group_id).
                 filter(model.Member.state == 'active').filter(model.Member.capacity == 'admin'))

    admins.update(set(model.Session.query(model.User).filter(model.User.sysadmin == True)))  # noqa

    return admins


def _get_ckan_admins():
    admins = set(model.Session.query(model.User).filter(model.User.sysadmin == True))  # noqa
    return admins
