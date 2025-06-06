from flask import Blueprint #type:ignore
from ckanext.ytp.request import utils

ytp_request = Blueprint('ytp_request', __name__)


def new(organization_id):
    return utils.new(organization_id)

def mylist(id):
    return utils.mylist(id)

def list():
    return utils.list()

def reject(mrequest_id):
    return utils.reject(mrequest_id)

def approve(mrequest_id):
    return utils.approve(mrequest_id)

def cancel(organization_id):
    return utils.cancel(organization_id)

def membership_cancel(organization_id):
    return utils.membership_cancel(organization_id)

def show(mrequest_id):
    return utils.show(mrequest_id)



ytp_request.add_url_rule("/member-request/new/<organization_id>", view_func=new, methods=['GET', 'POST'])
ytp_request.add_url_rule("/member-request/mylist/<id>", view_func=mylist, methods=['GET', 'POST'] )
ytp_request.add_url_rule("/member-request/list/", view_func=list,  methods=['GET', 'POST'] )
ytp_request.add_url_rule("/member-request/reject/<mrequest_id>", view_func=reject,  methods=['GET', 'POST'])
ytp_request.add_url_rule("/member-request/approve/<mrequest_id>", view_func=approve,  methods=['GET', 'POST'] )
ytp_request.add_url_rule("/member-request/cancel/<organization_id>", view_func=cancel, methods=['GET', 'POST'])
ytp_request.add_url_rule("/member-request/membership-cancel/<organization_id>", view_func=membership_cancel, methods=['GET', 'POST'])
ytp_request.add_url_rule("/member-request/<mrequest_id>", view_func=show, methods=['GET', 'POST'])