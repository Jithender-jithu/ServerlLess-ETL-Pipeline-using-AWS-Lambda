# ServerlLess-ETL-Pipeline-using-AWS-Lambda
A fully serverless, event-driven ETL pipeline built on AWS managed services — no servers to provision, no clusters to manage. This pipeline automatically extracts data from external REST APIs on a scheduled basis, transforms it using Python, stages it in Amazon S3, and loads it into Amazon RDS (PostgreSQL) with optimized indexing for analytical queries.
Designed for cost efficiency (pay-per-invocation), elastic scalability, and zero-maintenance infrastructure — ideal for ingesting market data, alternative datasets, or any external API feed.

# Architecture
┌──────────────────┐
│  Amazon          │
│  EventBridge     │  ← Cron schedule (e.g., every 6h)
│  (Scheduler)     │
└────────┬─────────┘
         │ Triggers
         ▼
┌──────────────────┐       ┌─────────────────┐
│  AWS Lambda      │──────▶│  External APIs  │
│  (Python 3.9)   │  GET   │  (REST / JSON)  │
│  Extractor Fn    │◀──────│                 │
└────────┬─────────┘       └─────────────────┘
         │ Raw JSON
         ▼
┌──────────────────┐
│  Amazon S3       │  ← Staging / archive layer
│  (Raw Staging)   │
└────────┬─────────┘
         │ Triggers
         ▼
┌──────────────────┐
│  AWS Lambda      │  ← Transform & validate
│  (Python 3.9)   │
│  Transform Fn    │
└────────┬─────────┘
         │ Clean records
         ▼
┌──────────────────┐
│  Amazon RDS      │  ← Persistent analytical store
│  (PostgreSQL)    │
│  Indexed + Tuned │
└──────────────────┘

# Tech Stack
Component        Technology
ComputeAWS       Lambda (Python 3.9, serverless)
Scheduling       Amazon EventBridge (cron rules)
Staging Storage  Amazon S3
Database         Amazon RDS (PostgreSQL 14)
Language         Python 3.9+
Libraries        boto3, psycopg2-binary, requests, pandas

# Prerequisites
AWS Account with Lambda, S3, RDS, EventBridge, and IAM permissions
AWS CLI configured (aws configure)
Python 3.9+ installed locally
PostgreSQL client (psql) for schema setup
