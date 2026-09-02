import os
import boto3
from decimal import Decimal
from src.common.aws_clients import get_dynamodb_resource

TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "rbsa-banking-table")

def create_table(dynamodb):
    try:
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},  # Partition Key
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}   # Sort Key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()
        print(f"Table {TABLE_NAME} created successfully.")
        return table
    except Exception as e:
        if "ResourceInUseException" in str(e):
            print(f"Table {TABLE_NAME} already exists.")
            return dynamodb.Table(TABLE_NAME)
        else:
            raise e

def seed_data(dynamodb):
    table = dynamodb.Table(TABLE_NAME)
    
    mock_items = [
        # Customer 1001 Profile & Data
        {
            "PK": "CUST#1001",
            "SK": "PROFILE",
            "name": "Alex Johnson",
            "phone": "+15550192834",
            "email": "alex.johnson@example.com",
            "kyc_status": "VERIFIED"
        },
        {
            "PK": "CUST#1001",
            "SK": "ACCOUNT#ACC-9876",
            "balance": Decimal('4520.50'),
            "type": "checking",
            "status": "ACTIVE"
        },
        {
            "PK": "CUST#1001",
            "SK": "ACCOUNT#ACC-5432",
            "balance": Decimal('12850.00'),
            "type": "savings",
            "status": "ACTIVE"
        },
        {
            "PK": "CUST#1001",
            "SK": "LOAN#LN-4421",
            "principal": Decimal('25000.00'),
            "balance": Decimal('18400.00'),
            "status": "APPROVED",
            "next_due_date": "2026-09-15"
        },
        {
            "PK": "CUST#1001",
            "SK": "CARD#CARD-8812",
            "last4": "8812",
            "status": "ACTIVE",
            "type": "DEBIT"
        },
        # Customer 1002 Profile & Data
        {
            "PK": "CUST#1002",
            "SK": "PROFILE",
            "name": "Maria Garcia",
            "phone": "+15550183344",
            "email": "maria.garcia@example.com",
            "kyc_status": "VERIFIED"
        },
        {
            "PK": "CUST#1002",
            "SK": "ACCOUNT#ACC-1122",
            "balance": Decimal('1250.75'),
            "type": "checking",
            "status": "ACTIVE"
        },
        {
            "PK": "CUST#1002",
            "SK": "CARD#CARD-3344",
            "last4": "3344",
            "status": "ACTIVE",
            "type": "CREDIT"
        }
    ]
    
    with table.batch_writer() as batch:
        for item in mock_items:
            batch.put_item(Item=item)
            
    print(f"Successfully seeded {len(mock_items)} records into {TABLE_NAME}.")

if __name__ == "__main__":
    dynamodb = get_dynamodb_resource()
    create_table(dynamodb)
    seed_data(dynamodb)
