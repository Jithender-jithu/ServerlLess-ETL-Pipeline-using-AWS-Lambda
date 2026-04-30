# lambda/transformer/handler.py
import json
import boto3
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone
import os

s3 = boto3.client('s3')

DB_CONFIG = {
    'host':     os.environ['RDS_HOST'],
    'port':     int(os.environ.get('RDS_PORT', 5432)),
    'dbname':   os.environ['RDS_DB'],
    'user':     os.environ['RDS_USER'],
    'password': os.environ['RDS_PASSWORD'],
}


def transform_record(raw: dict) -> dict | None:
    """Validate and transform a single raw record. Returns None to drop."""
    record_id = raw.get('id')
    amount    = raw.get('amount')

    # --- Data Quality Gates ---
    if not record_id:
        return None
    if amount is None or float(amount) <= 0:
        return None

    return {
        'source_api':   'external_api_v1',
        'record_id':    str(record_id),
        'payload':      json.dumps(raw),
        'amount':       float(amount),
        'category':     raw.get('category', 'UNKNOWN'),
        'status':       raw.get('status', 'PENDING'),
        'event_date':   raw.get('date'),
        'processed_at': datetime.now(timezone.utc),
    }


def handler(event, context):
    """Triggered by S3 event: transforms and loads data into RDS."""
    bucket = event['Records'][0]['s3']['bucket']['name']
    key    = event['Records'][0]['s3']['object']['key']

    # Read raw JSON from S3
    obj      = s3.get_object(Bucket=bucket, Key=key)
    records  = json.loads(obj['Body'].read())

    # Transform & validate
    cleaned  = [r for raw in records if (r := transform_record(raw)) is not None]
    dropped  = len(records) - len(cleaned)
    print(f"Transformed: {len(cleaned)} valid, {dropped} dropped.")

    if not cleaned:
        return {'statusCode': 200, 'loaded': 0}

    # Bulk upsert into RDS
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO api_records
                    (source_api, record_id, payload, amount, category, status, event_date, processed_at)
                VALUES %s
                ON CONFLICT (record_id) DO UPDATE SET
                    amount       = EXCLUDED.amount,
                    status       = EXCLUDED.status,
                    processed_at = EXCLUDED.processed_at
                """,
                [(r['source_api'], r['record_id'], r['payload'], r['amount'],
                  r['category'], r['status'], r['event_date'], r['processed_at'])
                 for r in cleaned],
                page_size=500
            )
        conn.commit()
        print(f"Loaded {len(cleaned)} records into RDS.")
        return {'statusCode': 200, 'loaded': len(cleaned)}
    finally:
        conn.close()
