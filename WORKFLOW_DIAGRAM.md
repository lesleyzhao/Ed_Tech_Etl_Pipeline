# Ed-Tech ETL Pipeline Workflow Diagram

## Complete System Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    ED-TECH ETL PIPELINE WORKFLOW                                │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

START: User runs deployment
│
├─ 1. DEPLOYMENT PHASE
│   │
│   ├─ deploy.sh (Entry Point)
│   │   ├─ Install dependencies (requirements.txt)
│   │   ├─ Deploy infrastructure (infrastructure/)
│   │   ├─ Upload ETL script to S3
│   │   ├─ Setup monitoring (monitoring/)
│   │   └─ Create sample data
│   │
│   └─ infrastructure/
│       ├─ app.py (CDK App Entry)
│       ├─ ed_tech_etl_stack.py (AWS Resources)
│       └─ cdk.json (CDK Configuration)
│
├─ 2. CONFIGURATION PHASE
│   │
│   └─ config/settings.yaml (Configuration)
│       ├─ AWS settings
│       ├─ Data source credentials
│       ├─ ETL parameters
│       └─ Monitoring settings
│
├─ 3. ETL PIPELINE EXECUTION
│   │
│   └─ etl/run_pipeline.py (Main ETL Orchestrator)
│       ├─ Load configuration
│       ├─ Initialize data sources
│       ├─ Extract data
│       ├─ Transform data
│       ├─ Load to S3
│       └─ Create search index
│       │
│       ├─ DATA EXTRACTION
│       │   ├─ etl/data-sources/oracle_connector.py
│       │   │   ├─ Connect to Oracle DB
│       │   │   ├─ Extract students, courses, enrollments
│       │   │   └─ Validate data quality
│       │   │
│       │   ├─ etl/data-sources/workday_connector.py
│       │   │   ├─ Authenticate with Workday API
│       │   │   ├─ Extract students, programs, jobs
│       │   │   └─ Get job matches
│       │   │
│       │   └─ etl/data-sources/tableau_connector.py
│       │       ├─ Authenticate with Tableau Server
│       │       ├─ Extract analytics data
│       │       └─ Get job market trends
│       │
│       ├─ DATA TRANSFORMATION
│       │   └─ etl/transformations/data_transformer.py
│       │       ├─ Clean and validate data
│       │       ├─ Create unified student profiles
│       │       ├─ Generate job recommendations
│       │       └─ Calculate data quality scores
│       │
│       └─ AWS GLUE ETL
│           └─ etl/glue/etl_script.py
│               ├─ Process 1M+ records
│               ├─ Transform and join data
│               ├─ Create search index
│               └─ Load to S3 Data Lake
│
├─ 4. DATA STORAGE
│   │
│   └─ AWS S3 Data Lake
│       ├─ Raw data (raw/)
│       ├─ Processed data (processed/)
│       └─ Search index (search-index/)
│
├─ 5. SEARCH & API LAYER
│   │
│   └─ lambda/search_handler.py (Lambda Function)
│       ├─ Load search index from S3
│       ├─ Process search requests
│       ├─ Generate recommendations
│       └─ Return JSON responses
│
├─ 6. MONITORING & OBSERVABILITY
│   │
│   └─ monitoring/cloudwatch_dashboard.py
│       ├─ Create CloudWatch dashboards
│       ├─ Setup alarms and alerts
│       ├─ Send custom metrics
│       └─ Monitor system health
│
└─ END: System ready for queries and recommendations

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    USER INTERACTION FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

User Query → Lambda Function → Search Index → S3 Data Lake → Response

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA FLOW DIAGRAM                                           │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

Data Sources → ETL Pipeline → S3 Data Lake → Search Index → Lambda API → User

Oracle DB ──┐
Workday API ─┼─→ run_pipeline.py ──→ data_transformer.py ──→ etl_script.py ──→ S3 ──→ search_handler.py
Tableau ────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FILE DEPENDENCY TREE                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

deploy.sh (START)
│
├─ requirements.txt
├─ config/settings.yaml
│
├─ infrastructure/
│   ├─ app.py
│   ├─ ed_tech_etl_stack.py
│   └─ cdk.json
│
├─ etl/run_pipeline.py (Main ETL Entry)
│   ├─ config/settings.yaml
│   ├─ etl/data-sources/oracle_connector.py
│   ├─ etl/data-sources/workday_connector.py
│   ├─ etl/data-sources/tableau_connector.py
│   ├─ etl/transformations/data_transformer.py
│   └─ etl/glue/etl_script.py
│
├─ lambda/search_handler.py (Search API)
│   └─ S3 Data Lake (search-index/)
│
├─ monitoring/cloudwatch_dashboard.py
│
└─ tests/ (Testing)
    ├─ test_etl_pipeline.py
    └─ test_search_function.py

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    EXECUTION SEQUENCE                                          │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

1. DEPLOYMENT (One-time)
   deploy.sh → infrastructure/ → AWS Resources Created

2. ETL EXECUTION (Scheduled/Manual)
   etl/run_pipeline.py → data-sources/ → transformations/ → glue/ → S3

3. SEARCH QUERIES (Real-time)
   User Request → lambda/search_handler.py → S3 → Response

4. MONITORING (Continuous)
   monitoring/ → CloudWatch → Alerts & Dashboards

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    KEY FILE ROLES                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

ENTRY POINTS:
├─ deploy.sh                    → Initial deployment and setup
├─ etl/run_pipeline.py         → ETL pipeline execution
└─ lambda/search_handler.py    → Search API endpoint

CONFIGURATION:
└─ config/settings.yaml        → All system configuration

DATA PROCESSING:
├─ etl/data-sources/           → Data extraction from external systems
├─ etl/transformations/        → Data cleaning and transformation
└─ etl/glue/                   → AWS Glue ETL processing

INFRASTRUCTURE:
└─ infrastructure/             → AWS CDK infrastructure definition

MONITORING:
└─ monitoring/                 → CloudWatch dashboards and alerts

TESTING:
└─ tests/                      → Unit and integration tests

SAMPLE DATA:
└─ data/                       → Sample data for testing
