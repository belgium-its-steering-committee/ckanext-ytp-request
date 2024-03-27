# coding=utf-8
import json
import logging
import uuid
from datetime import datetime
from ckan.common import config

import boto3

log = logging.getLogger(__name__)


def send_sqs_message(user, subject, message):
    # Create SQS client
    sqs = boto3.client('sqs',
                       region_name=config.get('ckan.sqs.region_id'),
                       aws_access_key_id=config.get('ckan.sqs.access_key'),
                       aws_secret_access_key=config.get('ckan.sqs.secret_key')
                       )
    now = datetime.now()
    current_time = now.strftime("%d-%m-%Y, %H:%M:%S")

    if (user.email is None) or not len(user.email):
        log.warn("No recipient email address available for {0}".format(user.display_name))
    else:
        message_body = {
            'display_name': user.display_name,
            'email': user.email,
            'subject': subject,
            'message': message
        }
        # Send message to SQS queue
        response = sqs.send_message(
            QueueUrl=config.get('ckan.sqs.queue_url'),
            MessageGroupId='notify_sysadmin',
            MessageDeduplicationId=str(uuid.uuid4()),
            MessageAttributes={
                'msg_ts': {
                    'DataType': 'String',
                    'StringValue': current_time
                }
            },
            MessageBody=json.dumps(message_body)
        )

        print('\t\n RESPONSE SQS_ID::',response['MessageId'],'\n')
