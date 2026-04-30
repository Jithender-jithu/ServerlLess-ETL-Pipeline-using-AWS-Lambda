# lambda/extractor/handler.py
import json
import boto3
import requests
from datetime import datetime, timezone
import os

s3 = boto3.client('s3')

BUCKET     = os.environ['STAGING_BUCKET']
API_URL    = os.environ['API_URL']
API_KEY    = os.environ['API_KEY']   # Store in AWS Secrets Manager


def handler(event, context):
    """Extract data from external API and stage to S3."""
    timestamp = datetime.now(timezone.utc).strftime('%Y/%m/%d/%H%M%S')

    try:
        response = requests.get(
            API_URL,
            headers={'Authorization': f'Bearer {API_KEY}'},
            timeout=30
        )
        response.raise_for_status()
        records = response.json()

        # Stage raw JSON to S3
        key = f"raw/{timestamp}/extract.json"
        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=json.dumps(records),
            ContentType='application/json'
        )

        print(f"Staged {len(records)} records → s3://{BUCKET}/{key}")
        return {'statusCode': 200, 'records_extracted': len(records), 's3_key': key}

    except requests.exceptions.RequestException as e:
        print(f"API extraction failed: {e}")
        raise
