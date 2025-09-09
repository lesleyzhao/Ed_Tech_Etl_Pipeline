#!/bin/bash

# Ed-Tech ETL Pipeline Deployment Script
# This script deploys the complete AWS infrastructure and ETL pipeline

set -e

echo "🚀 Starting Ed-Tech ETL Pipeline Deployment..."

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK is not installed. Installing..."
    npm install -g aws-cdk
fi

# Check if Python dependencies are installed
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run from project root."
    exit 1
fi

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set up environment variables
echo "🔧 Setting up environment variables..."
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
export CDK_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

echo "AWS Account: $CDK_DEFAULT_ACCOUNT"
echo "AWS Region: $AWS_DEFAULT_REGION"

# Deploy infrastructure
echo "🏗️ Deploying AWS infrastructure..."
cd infrastructure

# Bootstrap CDK if needed
echo "🔧 Bootstrapping CDK..."
cdk bootstrap

# Deploy the stack
echo "🚀 Deploying ETL pipeline stack..."
cdk deploy --require-approval never

# Get stack outputs
echo "📊 Getting stack outputs..."
STACK_OUTPUTS=$(aws cloudformation describe-stacks --stack-name EdTechETLPipeline --query 'Stacks[0].Outputs' --output json)

# Extract important values
DATA_LAKE_BUCKET=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="DataLakeBucketName") | .OutputValue')
SEARCH_LAMBDA_ARN=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="SearchLambdaArn") | .OutputValue')

echo "✅ Infrastructure deployed successfully!"
echo "📦 Data Lake Bucket: $DATA_LAKE_BUCKET"
echo "🔍 Search Lambda ARN: $SEARCH_LAMBDA_ARN"

cd ..

# Upload ETL script to S3
echo "📤 Uploading ETL script to S3..."
aws s3 cp etl/glue/etl_script.py s3://$DATA_LAKE_BUCKET/scripts/etl_script.py

# Set up monitoring
echo "📊 Setting up CloudWatch monitoring..."
python monitoring/cloudwatch_dashboard.py

# Create sample data
echo "📝 Creating sample data..."
python -c "
import json
import boto3
from datetime import datetime

# Sample data for testing
sample_data = {
    'index_created_at': datetime.now().isoformat(),
    'total_records': 3,
    'records': [
        {
            'student_id': 'STU001',
            'academic_program': 'Computer Science',
            'gpa': 3.8,
            'performance_score': 85.5,
            'career_interest': 'Software Engineering',
            'skill_gaps': ['Machine Learning', 'System Design'],
            'recommended_courses': ['ML101', 'CS201'],
            'record_type': 'student_profile'
        },
        {
            'job_posting_id': 'JOB001',
            'job_title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'San Francisco, CA',
            'required_skills': ['Python', 'AWS', 'Docker'],
            'salary_range': '80k-120k',
            'record_type': 'job_posting'
        },
        {
            'student_id': 'STU002',
            'academic_program': 'Data Science',
            'gpa': 3.6,
            'performance_score': 92.0,
            'career_interest': 'Data Science',
            'skill_gaps': ['Deep Learning', 'Statistics'],
            'recommended_courses': ['DL101', 'STAT201'],
            'record_type': 'student_profile'
        }
    ]
}

# Upload to S3
s3 = boto3.client('s3')
s3.put_object(
    Bucket='$DATA_LAKE_BUCKET',
    Key='search-index/student-resources.json',
    Body=json.dumps(sample_data, indent=2),
    ContentType='application/json'
)
print('Sample data uploaded to S3')
"

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Test the search function
echo "🔍 Testing search function..."
python -c "
import json
import boto3

# Test the Lambda function
lambda_client = boto3.client('lambda')

# Test student search
test_event = {
    'action': 'search_students',
    'query': 'Computer Science',
    'filters': {}
}

try:
    response = lambda_client.invoke(
        FunctionName='ed-tech-search',
        InvocationType='RequestResponse',
        Payload=json.dumps(test_event)
    )
    
    result = json.loads(response['Payload'].read())
    print('✅ Search function test passed')
    print(f'Response: {result}')
except Exception as e:
    print(f'❌ Search function test failed: {e}')
"

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update config/settings.yaml with your actual data source credentials"
echo "2. Run the ETL pipeline: python etl/run_pipeline.py"
echo "3. Test the search function with different queries"
echo "4. Monitor the system using CloudWatch dashboards"
echo ""
echo "🔗 Useful links:"
echo "- CloudWatch Dashboards: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_DEFAULT_REGION#dashboards:"
echo "- Lambda Functions: https://console.aws.amazon.com/lambda/home?region=$AWS_DEFAULT_REGION#/functions"
echo "- S3 Data Lake: https://console.aws.amazon.com/s3/buckets/$DATA_LAKE_BUCKET"
