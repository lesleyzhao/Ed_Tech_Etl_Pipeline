# Ed-Tech ETL Pipeline & Search Platform

A prototype project demonstrating AWS-based ETL pipeline and search functionality for an educational technology platform that matches students with suitable resources like job postings.

## 🏗️ Architecture Overview

This project replicates a production system that:
- Extracts data from multiple sources (Oracle, Workday, Tableau)
- Processes 1M+ records through AWS Glue ETL pipeline
- Stores data in S3 for scalable access
- Provides serverless search via AWS Lambda
- Monitors system performance with CloudWatch

## 🚀 Key Features

- **Distributed ETL Pipeline**: AWS Glue-based data processing
- **Multi-Source Data Ingestion**: Oracle, Workday, Tableau integration
- **Serverless Search**: AWS Lambda with 16% query time reduction
- **Real-time Monitoring**: CloudWatch dashboards and alerts
- **Scalable Storage**: S3-based data lake architecture
- **Student-Resource Matching**: AI-powered recommendation engine

## 📁 Project Structure

```
├── infrastructure/           # AWS CDK/Terraform infrastructure
├── etl/                     # ETL pipeline code
│   ├── glue/               # AWS Glue jobs
│   ├── data-sources/       # Source system integrations
│   └── transformations/    # Data transformation logic
├── lambda/                 # Serverless search functions
├── monitoring/             # CloudWatch dashboards & alerts
├── data/                   # Sample data and schemas
├── tests/                  # Unit and integration tests
└── docs/                   # Documentation
```

## 🛠️ Tech Stack

- **AWS Services**: Glue, Lambda, S3, CloudWatch, IAM
- **Languages**: Python, SQL, YAML
- **Infrastructure**: AWS CDK (TypeScript)
- **Data Sources**: Oracle, Workday, Tableau APIs
- **Monitoring**: CloudWatch, X-Ray

## 🚀 Quick Start

1. **Prerequisites**
   ```bash
   npm install -g aws-cdk
   pip install -r requirements.txt
   ```

2. **Deploy Infrastructure**
   ```bash
   cd infrastructure
   cdk deploy
   ```

3. **Run ETL Pipeline**
   ```bash
   python etl/run_pipeline.py
   ```

4. **Test Search Function**
   ```bash
   python lambda/test_search.py
   ```

## 📊 Performance Metrics

- **Data Volume**: 1M+ records processed
- **Query Performance**: 16% reduction in search time
- **Scalability**: Handles increasing data volume
- **Monitoring**: Real-time system visibility

## 🔧 Configuration

Update `config/settings.yaml` with your AWS credentials and data source configurations.

## 📈 Monitoring

Access CloudWatch dashboards to monitor:
- ETL job execution status
- Lambda function performance
- S3 storage metrics
- System health indicators

## 🤝 Contributing

This is a learning prototype. Feel free to fork and experiment with different AWS services and configurations.

## 📝 License

MIT License - See LICENSE file for details
