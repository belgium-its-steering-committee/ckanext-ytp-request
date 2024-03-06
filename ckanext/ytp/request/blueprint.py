from flask import Blueprint
import ckanext.ytp.request.utils as utils

ytp_request = Blueprint('ytp_request', __name__)


def new(organization_id, errors=None, error_summary=None):
    return utils.new(organization_id, errors, error_summary)

def mylist():
    return utils.mylist()

def list():
    return utils.list()

def reject():
    return utils.reject()

def approve():
    return utils.approve()

def cancel(organization_id, errors=None, error_summary=None):
    return utils.cancel(organization_id, errors, error_summary)

def membership_cancel(organization_id, errors=None, error_summary=None):
    return utils.membership_cancel(organization_id, errors, error_summary)

def show():
    return utils.show()



ytp_request.add_url_rule("/member-request/new/<organization_id>", view_func=new)
ytp_request.add_url_rule("/member-request/mylist", view_func=mylist)
ytp_request.add_url_rule("/member-request/list", view_func=list)
ytp_request.add_url_rule("/member-request/reject/{mrequest_id}", view_func=reject)
ytp_request.add_url_rule("/member-request/approve/{mrequest_id}", view_func=approve)
ytp_request.add_url_rule("/member-request/cancel", view_func=cancel)
ytp_request.add_url_rule("/member-request/membership-cancel/<organization_id>", view_func=membership_cancel)
ytp_request.add_url_rule("/member-request/{mrequest_id}", view_func=show)