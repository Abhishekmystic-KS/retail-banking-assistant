import pytest
import os
from decimal import Decimal
from unittest.mock import MagicMock, patch

from src.handlers.check_balance import lambda_handler as check_balance_handler
from src.handlers.report_lost_card import lambda_handler as report_lost_card_handler
from src.handlers.loan_status import lambda_handler as loan_status_handler

@patch('src.handlers.check_balance.get_dynamodb_resource')
def test_check_balance_handler_success(mock_get_db):
    mock_table = MagicMock()
    mock_get_db.return_value.Table.return_value = mock_table
    
    mock_table.query.return_value = {
        'Items': [
            {'SK': 'ACCOUNT#ACC-9876', 'type': 'checking', 'balance': Decimal('4520.50')}
        ]
    }
    
    event = {
        'sessionState': {
            'intent': {
                'name': 'CheckBalance',
                'slots': {
                    'CustomerId': {'value': {'interpretedValue': '1001'}},
                    'AccountType': {'value': {'interpretedValue': 'checking'}}
                }
            }
        }
    }
    
    res = check_balance_handler(event, None)
    assert res['sessionState']['intent']['state'] == 'Fulfilled'
    assert "$4,520.50" in res['messages'][0]['content']

@patch('src.handlers.report_lost_card.get_cloudwatch_client')
@patch('src.handlers.report_lost_card.get_dynamodb_resource')
def test_report_lost_card_handler(mock_get_db, mock_get_cw):
    mock_table = MagicMock()
    mock_get_db.return_value.Table.return_value = mock_table
    
    mock_table.query.return_value = {
        'Items': [
            {'PK': 'CUST#1001', 'SK': 'CARD#CARD-8812', 'last4': '8812', 'status': 'ACTIVE'}
        ]
    }
    
    event = {
        'sessionState': {
            'intent': {
                'name': 'ReportLostCard',
                'slots': {
                    'CustomerId': {'value': {'interpretedValue': '1001'}},
                    'CardLastFour': {'value': {'interpretedValue': '8812'}}
                }
            }
        }
    }
    
    res = report_lost_card_handler(event, None)
    assert res['sessionState']['intent']['state'] == 'Fulfilled'
    assert "ending in 8812 has been deactivated" in res['messages'][0]['content']
    mock_table.update_item.assert_called_once()
    mock_get_cw.return_value.put_metric_data.assert_called_once()

@patch('src.handlers.loan_status.get_dynamodb_resource')
def test_loan_status_handler(mock_get_db):
    mock_table = MagicMock()
    mock_get_db.return_value.Table.return_value = mock_table
    
    mock_table.query.return_value = {
        'Items': [
            {'SK': 'LOAN#LN-4421', 'status': 'APPROVED', 'balance': Decimal('18400.00'), 'next_due_date': '2026-09-15'}
        ]
    }
    
    event = {
        'sessionState': {
            'intent': {
                'name': 'LoanStatusInquiry',
                'slots': {
                    'CustomerId': {'value': {'interpretedValue': '1001'}}
                }
            }
        }
    }
    
    res = loan_status_handler(event, None)
    assert res['sessionState']['intent']['state'] == 'Fulfilled'
    assert "Loan ID LN-4421 Status: APPROVED" in res['messages'][0]['content']
