import json

def handler(request, response):
    return {
        "statusCode": 200,
        "headers": { "Content-Type": "application/json" },
        "body": json.dumps({
            "project": "Retail Banking Self-Service Assistant",
            "architecture": "AWS Serverless (Lambda, DynamoDB, S3, CloudWatch, Lex V2, Connect)",
            "local_setup": "Run ./scripts/deploy_local.sh with LocalStack"
        })
    }
