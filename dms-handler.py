import json
import logging
import re

import base64
import boto3
import datetime
import os
from aws_xray_sdk.core import patch_all, xray_recorder
from boto3_type_annotations.lambda_ import Client as Client
from pathlib import Path
from typing import List, Dict

patch_all()
boto3.set_stream_logger('', logging.INFO)


@xray_recorder.capture('invoke')
def handler(event, context):
    logging.info(repr(event))
    lamb: Client = boto3.client('lambda')
    resp = []
    for record in event["Records"]:
        message = json.loads(record["Sns"]["Message"])
        identifier_link = message["Identifier Link"]
        task_name = re.search(r"(?<=SourceId:).*$", identifier_link).group(0)
        print(task_name)
        event_message = message["Event Message"]

        current_time = f"{datetime.datetime.utcnow().isoformat(timespec='minutes')}Z"
        payload = {
            "message_type": "teams",
            "web_hook_url": os.getenv('TEAMS_URL'),
            "subject": f"DMS Task: {task_name} failed",
            "body": f"Event message received: {event_message} at {current_time}"
        }

        lambda_name = os.getenv('NOTIFY_LAMBDA_NAME')
        res = lamb.invoke(FunctionName=lambda_name, Payload=json.dumps(payload))
        if res.get('FunctionError') is not None:
            raise RuntimeError(f'{lambda_name} failed to notify with {payload}')
        else:
            resp.append(res)
    return resp


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--event', help='Path to event json file', type=Path)
    args = parser.parse_args()
    with open(args.event) as event_file:
        evt = json.load(event_file)
    handler(evt, {})
