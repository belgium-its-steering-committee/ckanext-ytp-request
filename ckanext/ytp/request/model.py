import uuid
import datetime
import six

from ckan import model
from ckan.model.meta import metadata as ckan_metadata #type: ignore
from ckan.plugins import toolkit #type:ignore

from sqlalchemy import Column, ForeignKey #type:ignore
from sqlalchemy import types #type:ignore
from sqlalchemy.ext.declarative import declarative_base #type:ignore


import logging
log = logging.getLogger(__name__)

Base = declarative_base(metadata=ckan_metadata)

"""CANCEL state is equivalent to DELETE state in member table.
member - member_request is one to many relationship since we need to log all member_requests to facilitate admins and users
what has happened with his previous requests """
REQUEST_PENDING = "pending"
REQUEST_ACCEPTED = "accepted"
REQUEST_REJECTED = "rejected"
REQUEST_CANCEL = "cancel"


def make_uuid():
    return six.text_type(uuid.uuid4())


class MemberRequest(Base):
    """
    Represents a member request containing request date, handled date,
    status (pending, approved,rejected, cancel) and language used by the member
    so that a localized e-mail could be sent
    Member request stores the request history while member table represents the current state a member has with
    a given organization
    """
    __tablename__ = 'member_request'

    id = Column(types.UnicodeText, primary_key=True, default=make_uuid)
    # Reference to the table containing the composite key for organization and
    # user
    membership_id = Column(types.UnicodeText, ForeignKey(model.Member.id))
    request_date = Column(types.DateTime, default=datetime.datetime.now)
    role = Column(types.UnicodeText)
    handling_date = Column(types.DateTime)
    handled_by = Column(types.UnicodeText)
    language = Column(types.UnicodeText)
    message = Column(types.UnicodeText)
    status = Column(types.UnicodeText, default=u"pending")

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def init_tables():
    #methods checks for table existence
    try:
        Base.metadata.create_all(model.meta.engine)
    except:
        toolkit.abort(500, detail=toolkit.u(u"Membership request tables not created in database"))