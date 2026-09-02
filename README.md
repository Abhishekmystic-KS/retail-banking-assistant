# Retail Banking Self-Service Assistant (AWS Serverless, LocalStack-first)

[![CI Pipeline](https://github.com/Abhishekmystic-KS/retail-banking-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/Abhishekmystic-KS/retail-banking-assistant/actions)

A resume-grade, portfolio project demonstrating hands-on AWS serverless engineering for retail banking use cases: **Lambda, DynamoDB, S3, CloudWatch, Lex V2, and Amazon Connect**.

Developed locally via **LocalStack** to eliminate cloud costs and provisioning delays, backed by GitHub Actions CI integration.

---

## 🏗️ Architecture

```
Customer (Voice / Chat)
      │
      ▼
  Amazon Connect (Contact Flow & IVR Routing)
      │
      ▼
  Amazon Lex V2 (Intent Recognition & NLU)
      │
      ├──▶ CheckBalance Intent
      ├──▶ ReportLostCard Intent
      ├──▶ LoanStatusInquiry Intent
      └──▶ FallbackToAgent Intent
      │
      ▼
  AWS Lambda (Python Fulfillment Handlers)
      │
      ├──▶ DynamoDB (Single-Table Design: Profiles, Accounts, Loans, Cards)
      └──▶ Amazon S3 (Statement & KYC Document Storage + Glacier 90-Day Lifecycle)

  CloudWatch ── Custom Metric (`LostCardReports`) + Latency & Error Alarms
```

---

## 💾 Data Model (DynamoDB Single-Table Design)

Table Name: `rbsa-banking-table`

| Partition Key (PK) | Sort Key (SK) | Key Attributes |
|---|---|---|
| `CUST#<id>` | `PROFILE` | `name`, `phone`, `email`, `kyc_status` |
| `CUST#<id>` | `ACCOUNT#<acct_id>` | `balance`, `type` (checking/savings), `status` |
| `CUST#<id>` | `LOAN#<loan_id>` | `principal`, `balance`, `status`, `next_due_date` |
| `CUST#<id>` | `CARD#<card_id>` | `last4`, `status` (`ACTIVE`/`REPORTED_LOST`), `type` |

---

## ⚡ Lambda Fulfillment Handlers

| Function | Trigger | Responsibility |
|---|---|---|
| `checkBalanceHandler` | Lex `CheckBalance` intent | Queries DynamoDB single-table layout and returns formatted checking/savings balance. |
| `reportLostCardHandler` | Lex `ReportLostCard` intent | Updates card status to `REPORTED_LOST` in DynamoDB and emits custom CloudWatch metric (`LostCardReports`). |
| `loanStatusHandler` | Lex `LoanStatusInquiry` intent | Fetches active loan balance and next payment due date from DynamoDB. |
| `documentFetchHandler` | S3 event / Direct invocation | Fetches or uploads customer KYC documents / monthly statements to `rbsa-banking-docs`. |

---

## 📊 CloudWatch Metrics & Monitoring

- **Custom Metric**: `LostCardReports` (Count metric under namespace `RBSA/BankingMetrics`).
- **Alarm 1**: `rbsa-lambda-high-error-rate` (Triggers when any Lambda encounters execution errors in a 5 min window).
- **Alarm 2**: `rbsa-lambda-p99-latency-high` (Triggers when p99 Lambda latency exceeds 3000ms).

---

## 🚀 Quickstart (One-Command Local Setup)

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- `pip install -r requirements.txt`

### Run locally via LocalStack
```bash
./scripts/deploy_local.sh
```

### Run Unit Tests
```bash
pytest -v
```

---

## 🚀 Production / AWS Cloud Considerations

If promoting to a production environment:
1. **Security & Identity**: Add Amazon Cognito for user authentication and fine-grained IAM roles for each Lambda function.
2. **API Gateway / CloudFront**: Wrap document fetching in Amazon API Gateway with WAF protection.
3. **Infrastructure as Code**: Terraform or AWS CDK modules for reproducible stage/prod deployments.
