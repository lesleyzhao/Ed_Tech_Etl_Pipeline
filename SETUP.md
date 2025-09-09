# Ed-Tech ETL Pipeline Setup Guide

This guide will walk you through setting up and deploying the Ed-Tech ETL Pipeline prototype project.

## Prerequisites

### Required Software
- **Python 3.11+**: [Download here](https://www.python.org/downloads/)
- **Node.js 18+**: [Download here](https://nodejs.org/)
- **AWS CLI**: [Installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **AWS CDK**: `npm install -g aws-cdk`
- **Git**: [Download here](https://git-scm.com/downloads)

### AWS Account Setup
1. **Create AWS Account**: Sign up at [aws.amazon.com](https://aws.amazon.com)
2. **Configure AWS CLI**: Run `aws configure` with your credentials
3. **Set up IAM User**: Create a user with necessary permissions (see IAM section below)
4. **Choose Region**: This project defaults to `us-east-1`

### Required AWS Permissions
Your AWS user/role needs the following permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "glue:*",
                "lambda:*",
                "cloudwatch:*",
                "logs:*",
                "iam:*",
                "cloudformation:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ed-tech-etl-pipeline
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install AWS CDK
```bash
npm install -g aws-cdk
```

### 4. Bootstrap CDK (First time only)
```bash
cd infrastructure
cdk bootstrap
cd ..
```

## Configuration

### 1. Update Configuration File
Edit `config/settings.yaml` with your specific settings:

```yaml
# AWS Configuration
aws:
  region: us-east-1
  account_id: "YOUR_AWS_ACCOUNT_ID"  # Replace with your account ID

# Data Sources Configuration
data_sources:
  oracle:
    host: "your-oracle-host.com"
    port: 1521
    service_name: "YOUR_SERVICE"
    username: "${ORACLE_USERNAME}"
    password: "${ORACLE_PASSWORD}"
  
  workday:
    base_url: "https://your-workday-instance.com"
    tenant: "your-tenant"
    username: "${WORKDAY_USERNAME}"
    password: "${WORKDAY_PASSWORD}"
  
  tableau:
    server_url: "https://your-tableau-server.com"
    site_id: "your-site-id"
    username: "${TABLEAU_USERNAME}"
    password: "${TABLEAU_PASSWORD}"
```

### 2. Set Environment Variables
```bash
export ORACLE_USERNAME="your_oracle_username"
export ORACLE_PASSWORD="your_oracle_password"
export WORKDAY_USERNAME="your_workday_username"
export WORKDAY_PASSWORD="your_workday_password"
export TABLEAU_USERNAME="your_tableau_username"
export TABLEAU_PASSWORD="your_tableau_password"
```

## Deployment

### Option 1: Automated Deployment (Recommended)
```bash
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Deployment

#### 1. Deploy Infrastructure
```bash
cd infrastructure
cdk deploy
cd ..
```

#### 2. Upload ETL Script
```bash
# Get the bucket name from CDK output
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name EdTechETLPipeline --query 'Stacks[0].Outputs[?OutputKey==`DataLakeBucketName`].OutputValue' --output text)

# Upload the ETL script
aws s3 cp etl/glue/etl_script.py s3://$BUCKET_NAME/scripts/etl_script.py
```

#### 3. Set up Monitoring
```bash
python monitoring/cloudwatch_dashboard.py
```

#### 4. Create Sample Data
```bash
python -c "
import json
import boto3
from datetime import datetime

# Load sample data
with open('data/sample_workday_data.json', 'r') as f:
    sample_data = json.load(f)

# Upload to S3
s3 = boto3.client('s3')
bucket_name = 'ed-tech-data-lake-YOUR_ACCOUNT_ID'  # Replace with actual bucket name

s3.put_object(
    Bucket=bucket_name,
    Key='search-index/student-resources.json',
    Body=json.dumps(sample_data, indent=2),
    ContentType='application/json'
)
print('Sample data uploaded successfully!')
"
```

## Testing

### 1. Run Unit Tests
```bash
python -m pytest tests/ -v
```

### 2. Test ETL Pipeline
```bash
python etl/run_pipeline.py
```

### 3. Test Search Function
```bash
# Test student search
aws lambda invoke --function-name ed-tech-search --payload '{"action":"search_students","query":"Computer Science"}' response.json
cat response.json

# Test job search
aws lambda invoke --function-name ed-tech-search --payload '{"action":"search_jobs","query":"Software Engineer"}' response.json
cat response.json

# Test recommendations
aws lambda invoke --function-name ed-tech-search --payload '{"action":"get_recommendations","student_id":"STU001"}' response.json
cat response.json
```

## Usage

### 1. Running the ETL Pipeline
```bash
# Run the complete pipeline
python etl/run_pipeline.py

# Run with specific configuration
python etl/run_pipeline.py --config custom_config.yaml
```

### 2. Using the Search API
```python
import boto3
import json

# Initialize Lambda client
lambda_client = boto3.client('lambda')

# Search for students
search_event = {
    "action": "search_students",
    "query": "Computer Science",
    "filters": {
        "min_gpa": 3.5
    }
}

response = lambda_client.invoke(
    FunctionName='ed-tech-search',
    InvocationType='RequestResponse',
    Payload=json.dumps(search_event)
)

result = json.loads(response['Payload'].read())
print(result)
```

### 3. Monitoring the System
- **CloudWatch Dashboards**: Monitor ETL jobs and Lambda performance
- **CloudWatch Logs**: View detailed logs for troubleshooting
- **S3 Metrics**: Track data lake usage and costs

## Troubleshooting

### Common Issues

#### 1. CDK Bootstrap Error
```bash
# If you get a bootstrap error, run:
cdk bootstrap aws://YOUR_ACCOUNT_ID/us-east-1
```

#### 2. Permission Denied Errors
- Ensure your AWS credentials have the required permissions
- Check that your IAM user has the necessary policies attached

#### 3. Lambda Function Not Found
- Verify the function was created successfully
- Check the function name matches the configuration

#### 4. S3 Access Denied
- Ensure the Lambda execution role has S3 read/write permissions
- Check the bucket policy allows the Lambda function access

#### 5. Data Source Connection Issues
- Verify your database/API credentials are correct
- Check network connectivity and firewall rules
- Ensure the data sources are accessible from AWS

### Debugging Steps

1. **Check CloudWatch Logs**:
   ```bash
   aws logs describe-log-groups --log-group-name-prefix "/aws/ed-tech"
   ```

2. **Verify Infrastructure**:
   ```bash
   aws cloudformation describe-stacks --stack-name EdTechETLPipeline
   ```

3. **Test Individual Components**:
   ```bash
   # Test Oracle connection
   python -c "from etl.data_sources.oracle_connector import OracleConnector; print('Oracle connector imported successfully')"
   
   # Test Workday connection
   python -c "from etl.data_sources.workday_connector import WorkdayConnector; print('Workday connector imported successfully')"
   
   # Test Tableau connection
   python -c "from etl.data_sources.tableau_connector import TableauConnector; print('Tableau connector imported successfully')"
   ```

## Cost Management

### Estimated Monthly Costs (us-east-1)
- **S3 Storage**: ~$5-10 (50GB data lake)
- **Lambda**: ~$2-5 (100K requests)
- **Glue**: ~$10-20 (2 DPU hours)
- **CloudWatch**: ~$5-10 (logs and metrics)
- **Total**: ~$25-50/month

### Cost Optimization Tips
1. **Use S3 Lifecycle Policies**: Move old data to cheaper storage classes
2. **Optimize Glue Jobs**: Use appropriate DPU allocation
3. **Monitor Lambda Usage**: Set up billing alerts
4. **Clean Up Resources**: Delete unused stacks when not needed

## Security Best Practices

1. **Use IAM Roles**: Don't hardcode credentials
2. **Enable Encryption**: Use S3 server-side encryption
3. **Network Security**: Use VPC endpoints for private access
4. **Audit Logging**: Enable CloudTrail for all API calls
5. **Regular Updates**: Keep dependencies updated

## Next Steps

1. **Customize Data Sources**: Modify connectors for your specific systems
2. **Enhance Matching Logic**: Implement more sophisticated recommendation algorithms
3. **Add Real-time Processing**: Consider Kinesis for streaming data
4. **Implement ML**: Use SageMaker for advanced analytics
5. **Scale Up**: Add more data sources and increase processing capacity

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review CloudWatch logs for error details
3. Consult AWS documentation for specific services
4. Create an issue in the project repository

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
