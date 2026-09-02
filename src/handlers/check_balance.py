import os
import json
import logging
from src.common.aws_clients import get_dynamodb_resource

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "rbsa-banking-table")

def lambda_handler(event, context):
    """
    Amazon Lex V2 Fulfillment Handler for CheckBalance Intent.
    Expected Lex event contains sessionAttributes or slots (e.g., CustomerId, AccountType).
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Extract intent details from Lex V2 event structure
    intent_name = event.get('sessionState', {}).get('intent', {}).get('name', 'CheckBalance')
    slots = event.get('sessionState', {}).get('intent', {}).get('slots', {})
    
    # Extract customer ID from slots or default to demo customer
    cust_id_slot = slots.get('CustomerId', {})
    cust_id = cust_id_slot.get('value', {}).get('interpretedValue', '1001') if cust_id_slot else '1001'
    
    acct_type_slot = slots.get('AccountType', {})
    acct_type = acct_type_slot.get('value', {}).get('interpretedValue', 'checking').lower() if acct_type_slot else 'checking'

    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(TABLE_NAME)
    
    pk = f"CUST#{cust_id}"
    
    try:
        # Query items for customer accounts
        response = table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
            ExpressionAttributeValues={
                ":pk": pk,
                ":sk_prefix": "ACCOUNT#"
            }
        )
        
        items = response.get('Items', [])
        target_account = None
        
        for item in items:
            if item.get('type', '').lower() == acct_type:
                target_account = item
                break
        
        if not target_account and items:
            target_account = items[0] # Default to first account if specified type not found
            
        if target_account:
            balance = target_account.get('balance', 0.0)
            account_id = target_account.get('SK', '').replace('ACCOUNT#', '')
            acc_type_name = target_account.get('type', 'Account').capitalize()
            message = f"Your {acc_type_name} account ({account_id}) balance is ${float(balance):,.2f}."
        else:
            message = f"Sorry, no active account found for Customer ID {cust_id}."
            
    except Exception as e:
        logger.error(f"Error querying DynamoDB: {str(e)}")
        message = "Sorry, I am unable to retrieve your balance at this moment. Please try again later."

    # Return standard Lex V2 response format
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": intent_name,
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            }
        ]
    }
