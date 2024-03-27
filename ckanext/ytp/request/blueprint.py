from flask import Blueprint
import ckanext.ytp.request.utils as utils

ytp_request = Blueprint('ytp_request', __name__)


def new(organization_id, errors=None, error_summary=None):
    return utils.new(organization_id, errors, error_summary)

def mylist(id, errors=None, error_summary=None):
    return utils.mylist(id, errors, error_summary)

def list(organization_id, errors=None, error_summary=None):
    return utils.list(organization_id, errors, error_summary)

def reject(mrequest_id, errors=None, error_summary=None):
    return utils.reject(mrequest_id, errors, error_summary)

def approve(mrequest_id, errors=None, error_summary=None):
    return utils.approve(mrequest_id, errors, error_summary)

def cancel(organization_id, errors=None, error_summary=None):
    return utils.cancel(organization_id, errors, error_summary)

def membership_cancel(organization_id, errors=None, error_summary=None):
    return utils.membership_cancel(organization_id, errors, error_summary)

def show(mrequest_id, errors=None, error_summary=None):
    return utils.show(mrequest_id, errors, error_summary)



ytp_request.add_url_rule("/member-request/new/<organization_id>", view_func=new, methods=['GET', 'POST'])
ytp_request.add_url_rule("/member-request/mylist/<id>", view_func=mylist, methods=['GET', 'POST'] )
ytp_request.add_url_rule("/member-request/list/<organization_id>", view_func=list,  methods=['GET', 'POST'] )
ytp_request.add_url_rule("/member-request/reject/<mrequest_id>", view_func=reject,  methods=['GET', 'POST'])
ytp_request.add_url_rule("/member-request/approve/<mrequest_id>", view_func=approve,  methods=['GET', 'POST'] )
ytp_request.add_url_rule("/member-request/cancel/<organization_id>", view_func=cancel, methods=['GET', 'POST'])
ytp_request.add_url_rule("/member-request/membership-cancel/<organization_id>", view_func=membership_cancel, methods=['GET', 'POST'])
ytp_request.add_url_rule("/member-request/<mrequest_id>", view_func=show, methods=['GET', 'POST'])