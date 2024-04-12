import logging
import uuid
import six
from datetime import datetime
from ckan.plugins import toolkit #type:ignore
import boto3 #type:ignore

log = logging.getLogger(__name__)


def send_sqs_message(user, subject, message):
    # Create SQS client
    sqs = boto3.client('sqs',
                       region_name=toolkit.config.get('ckan.sqs.region_id'),
                       aws_access_key_id=toolkit.config.get('ckan.sqs.access_key'),
                       aws_secret_access_key=toolkit.config.get('ckan.sqs.secret_key')
                       )

    #messagesAttributes
    message_attributes = { 
            'sender_email':{
                'StringValue': str(toolkit.config.get('ckan.sqs.ytp.contact.email')),
                'DataType':'String' 
            },
            'reciever_email':{
                'StringValue': user.email,
                'DataType': 'String'
            },
            'display_name':{
                'StringValue': user.display_name,
                'DataType': 'String'
            },
            'subject':{
                'StringValue': subject,
                'DataType':'String'
            },
            'timeStamp':{
                'StringValue': datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
                'DataType': 'String'
            }
    }

    if (user.email is None) or not len(user.email):
        log.warn("No recipient email addMessageBodyMessageBodyress available for {0}".format(user.display_name))
    else:
        #TODO
        """
        cath sqs-lambda errors
        """
        response = sqs.send_message(
            QueueUrl = toolkit.config.get('ckan.sqs.queue_url'),
            MessageGroupId="Notify_admin",
            MessageDeduplicationId=six.text_type(uuid.uuid4()),
            MessageAttributes = message_attributes,
            MessageBody = message
        )
        log.info("YTP-request messages send. Response:: ", response)
          