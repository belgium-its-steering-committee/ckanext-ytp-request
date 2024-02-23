from flask import Bleuprint
import ckanext_ytp_request.utils as utils

ytp_request = Bleuprint('ytp_request', __name__)


def new():
    return utils.new()

def mylist():
    return utils.mylist()

def list():
    return utils.list()

def reject():
    return utils.reject()

def approve():
    return utils.approve()

def cancel():
    return utils.cancel()

def membership_cancel():
    return utils.membership_cancel()

def show():
    return utils.show()



ytp_request.add_url_rule("/member-request/new", view_func=new)
ytp_request.add_url_rule("/member-request/mylist", view_func=mylist)
ytp_request.add_url_rule("member-request/list", view_func=list)
ytp_request.add_url_rule("member-request/reject/{mrequest_id}", view_func=reject)
ytp_request.add_url_rule("member-request/approve/{mrequest_id}", view_func=approve)
ytp_request.add_url_rule("member-request/cancel", view_func=cancel)
ytp_request.add_url_rule("member-request/membership-cancel/{organization_id}", view_func=membership_cancel)
ytp_request.add_url_rule("member-request/{mrequest_id}", view_func=show)