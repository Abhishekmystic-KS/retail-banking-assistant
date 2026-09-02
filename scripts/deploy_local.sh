#!/bin/bash
set -e

echo "========================================================"
echo "🚀 Retail Banking Self-Service Assistant (RBSA) Setup"
echo "========================================================"

# Step 1: Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH."
    exit 1
fi

# Step 2: Start LocalStack container
echo "📦 Starting LocalStack via Docker Compose..."
docker-compose up -d

echo "⏳ Waiting for LocalStack to be ready..."
until curl -s http://localhost:4566/_localstack/health | grep -q '"dynamodb": "running"\|"dynamodb": "available"'; do
    sleep 2
    echo -n "."
done
echo ""
echo "✅ LocalStack is up and running!"

# Step 3: Seed DynamoDB Table
echo "📊 Seeding DynamoDB Single-Table schema & mock data..."
python3 -m scripts.seed_dynamodb

# Step 4: Provision S3 & CloudWatch Alarms
echo "☁️ Provisioning S3 Bucket with Glacier Lifecycle & CloudWatch Alarms..."
python3 -m scripts.setup_s3_cloudwatch

# Step 5: Run Tests
echo "🧪 Running unit & integration tests..."
pytest -v

echo "========================================================"
echo "🎉 Setup Complete! LocalStack infrastructure is live."
echo "========================================================"
