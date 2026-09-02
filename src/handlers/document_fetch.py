import os
import json
import logging
from src.common.aws_clients import get_s3_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "rbsa-banking-docs")

def lambda_handler(event, context):
    """
    On-demand or event-driven handler for fetching/storing customer documents (e.g. KYC, monthly statements).
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    doc_key = event.get('document_key', 'statements/1001_statement_august.pdf')
    action = event.get('action', 'GET')
    
    s3 = get_s3_client()
    
    try:
        if action == 'GET':
            response = s3.get_object(Bucket=BUCKET_NAME, Key=doc_key)
            content = response['Body'].read().decode('utf-8')
            return {
                'statusCode': 200,
                'body': json.dumps({'key': doc_key, 'content': content})
            }
        elif action == 'PUT':
            body_content = event.get('content', 'Sample statement document content.')
            s3.put_object(Bucket=BUCKET_NAME, Key=doc_key, Body=body_content.encode('utf-8'))
            return {
                'statusCode': 200,
                'body': json.dumps({'message': f"Document {doc_key} uploaded successfully to bucket {BUCKET_NAME}."})
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unsupported action.'})
            }
    except Exception as e:
        logger.error(f"Error handling S3 document: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
