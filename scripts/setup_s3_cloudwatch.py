import os
from src.common.aws_clients import get_s3_client, get_cloudwatch_client

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "rbsa-banking-docs")

def create_s3_bucket_with_lifecycle():
    s3 = get_s3_client()
    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket {BUCKET_NAME} created.")
    except Exception as e:
        print(f"Bucket creation note: {str(e)}")
        
    lifecycle_config = {
        'Rules': [
            {
                'ID': 'ArchiveOldStatements',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'statements/'},
                'Transitions': [
                    {
                        'Days': 90,
                        'StorageClass': 'GLACIER'
                    }
                ]
            }
        ]
    }
    
    try:
        s3.put_bucket_lifecycle_configuration(
            Bucket=BUCKET_NAME,
            LifecycleConfiguration=lifecycle_config
        )
        print(f"S3 Lifecycle Rule configured for {BUCKET_NAME} (Archive statements after 90 days to GLACIER).")
    except Exception as e:
        print(f"Error setting lifecycle rule: {str(e)}")

def create_cloudwatch_alarms():
    cw = get_cloudwatch_client()
    
    # Alarm 1: Lambda High Error Rate
    try:
        cw.put_metric_alarm(
            AlarmName='rbsa-lambda-high-error-rate',
            ComparisonOperator='GreaterThanOrEqualToThreshold',
            EvaluationPeriods=1,
            MetricName='Errors',
            Namespace='AWS/Lambda',
            Period=300,
            Statistic='Sum',
            Threshold=1.0,
            ActionsEnabled=False,
            AlarmDescription='Triggers when any Lambda function records an error over a 5-minute period.'
        )
        print("CloudWatch Alarm 'rbsa-lambda-high-error-rate' created.")
    except Exception as e:
        print(f"Error creating error alarm: {str(e)}")

    # Alarm 2: Lambda High Latency (Duration > 3000ms)
    try:
        cw.put_metric_alarm(
            AlarmName='rbsa-lambda-p99-latency-high',
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=1,
            MetricName='Duration',
            Namespace='AWS/Lambda',
            Period=300,
            ExtendedStatistic='p99',
            Threshold=3000.0,
            ActionsEnabled=False,
            AlarmDescription='Triggers when p99 Lambda invocation latency exceeds 3 seconds.'
        )
        print("CloudWatch Alarm 'rbsa-lambda-p99-latency-high' created.")
    except Exception as e:
        print(f"Error creating duration alarm: {str(e)}")

if __name__ == "__main__":
    create_s3_bucket_with_lifecycle()
    create_cloudwatch_alarms()
