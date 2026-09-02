import os
import json
import logging
from src.common.aws_clients import get_dynamodb_resource

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "rbsa-banking-table")

def lambda_handler(event, context):
    """
    Amazon Lex V2 Fulfillment Handler for LoanStatusInquiry Intent.
    Queries DynamoDB for customer's active loan details and returns status/next due date.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    intent_name = event.get('sessionState', {}).get('intent', {}).get('name', 'LoanStatusInquiry')
    slots = event.get('sessionState', {}).get('intent', {}).get('slots', {})
    
    cust_id_slot = slots.get('CustomerId', {})
    cust_id = cust_id_slot.get('value', {}).get('interpretedValue', '1001') if cust_id_slot else '1001'

    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(TABLE_NAME)
    pk = f"CUST#{cust_id}"
    
    try:
        # Query customer loans
        response = table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
            ExpressionAttributeValues={
                ":pk": pk,
                ":sk_prefix": "LOAN#"
            }
        )
        
        loans = response.get('Items', [])
        
        if loans:
            loan = loans[0]
            loan_id = loan['SK'].replace('LOAN#', '')
            status = loan.get('status', 'PENDING')
            balance = loan.get('balance', 0.0)
            due_date = loan.get('next_due_date', 'N/A')
            
            message = (f"Loan ID {loan_id} Status: {status}. "
                       f"Remaining Balance: ${float(balance):,.2f}. "
                       f"Next payment due date: {due_date}.")
        else:
            message = f"No active loan records found for Customer ID {cust_id}."
            
    except Exception as e:
        logger.error(f"Error checking loan status: {str(e)}")
        message = "Unable to retrieve loan information at this time. Please try again later."

    return {
        "sessionState": {
            "dialogAction": {"type": "Close"},
            "intent": {"name": intent_name, "state": "Fulfilled"}
        },
        "messages": [
            {"contentType": "PlainText", "content": message}
        ]
    }
