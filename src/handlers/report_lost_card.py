import os
import json
import logging
from src.common.aws_clients import get_dynamodb_resource, get_cloudwatch_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "rbsa-banking-table")

def lambda_handler(event, context):
    """
    Amazon Lex V2 Fulfillment Handler for ReportLostCard Intent.
    Updates card status in DynamoDB to 'REPORTED_LOST' and emits a custom CloudWatch metric.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    intent_name = event.get('sessionState', {}).get('intent', {}).get('name', 'ReportLostCard')
    slots = event.get('sessionState', {}).get('intent', {}).get('slots', {})
    
    cust_id_slot = slots.get('CustomerId', {})
    cust_id = cust_id_slot.get('value', {}).get('interpretedValue', '1001') if cust_id_slot else '1001'
    
    last4_slot = slots.get('CardLastFour', {})
    last4 = last4_slot.get('value', {}).get('interpretedValue', None) if last4_slot else None

    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(TABLE_NAME)
    pk = f"CUST#{cust_id}"
    
    try:
        # Query customer cards
        response = table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
            ExpressionAttributeValues={
                ":pk": pk,
                ":sk_prefix": "CARD#"
            }
        )
        
        cards = response.get('Items', [])
        target_card = None
        
        if last4:
            for c in cards:
                if c.get('last4') == last4:
                    target_card = c
                    break
        elif cards:
            target_card = cards[0] # Default to first card if last4 not specified
            
        if target_card:
            card_sk = target_card['SK']
            card_last4 = target_card.get('last4', 'xxxx')
            
            # Update status to REPORTED_LOST
            table.update_item(
                Key={'PK': pk, 'SK': card_sk},
                UpdateExpression="SET #st = :status",
                ExpressionAttributeNames={'#st': 'status'},
                ExpressionAttributeValues={':status': 'REPORTED_LOST'}
            )
            
            # Emit custom CloudWatch metric: LostCardReports
            cw = get_cloudwatch_client()
            try:
                cw.put_metric_data(
                    Namespace='RBSA/BankingMetrics',
                    MetricData=[
                        {
                            'MetricName': 'LostCardReports',
                            'Dimensions': [
                                {'Name': 'CustomerId', 'Value': cust_id}
                            ],
                            'Value': 1,
                            'Unit': 'Count'
                        }
                    ]
                )
                logger.info("Custom metric LostCardReports emitted to CloudWatch.")
            except Exception as cw_err:
                logger.warning(f"Failed to emit CloudWatch metric: {str(cw_err)}")
                
            message = f"Your card ending in {card_last4} has been deactivated and reported as lost/stolen. A replacement card will be issued to your address on file."
        else:
            message = f"No active cards were found associated with Customer ID {cust_id}."
            
    except Exception as e:
        logger.error(f"Error reporting lost card: {str(e)}")
        message = "We encountered an issue processing your lost card request. Please call customer support immediately."

    return {
        "sessionState": {
            "dialogAction": {"type": "Close"},
            "intent": {"name": intent_name, "state": "Fulfilled"}
        },
        "messages": [
            {"contentType": "PlainText", "content": message}
        ]
    }
