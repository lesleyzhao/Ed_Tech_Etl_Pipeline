"""
Main ETL Pipeline Runner for Ed-Tech Platform
Orchestrates data extraction, transformation, and loading
"""

import os
import sys
import yaml
import logging
import json
from datetime import datetime
from typing import Dict, Any
import boto3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from etl.data_sources.oracle_connector import OracleConnector
from etl.data_sources.workday_connector import WorkdayConnector
from etl.data_sources.tableau_connector import TableauConnector
from etl.transformations.data_transformer import DataTransformer
from monitoring.cloudwatch_dashboard import CloudWatchMonitoring

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EdTechETLPipeline:
    """Main ETL pipeline orchestrator"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self.load_config(config_path)
        self.s3_client = boto3.client('s3')
        self.monitoring = CloudWatchMonitoring()
        self.data_sources = {}
        self.processed_data = {}
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info("Configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise
    
    def initialize_data_sources(self):
        """Initialize connections to all data sources"""
        logger.info("Initializing data source connections...")
        
        try:
            # Initialize Oracle connector
            if 'oracle' in self.config['data_sources']:
                self.data_sources['oracle'] = OracleConnector(
                    self.config['data_sources']['oracle']
                )
                if not self.data_sources['oracle'].connect():
                    logger.warning("Failed to connect to Oracle")
            
            # Initialize Workday connector
            if 'workday' in self.config['data_sources']:
                self.data_sources['workday'] = WorkdayConnector(
                    self.config['data_sources']['workday']
                )
                if not self.data_sources['workday'].authenticate():
                    logger.warning("Failed to authenticate with Workday")
            
            # Initialize Tableau connector
            if 'tableau' in self.config['data_sources']:
                self.data_sources['tableau'] = TableauConnector(
                    self.config['data_sources']['tableau']
                )
                if not self.data_sources['tableau'].authenticate():
                    logger.warning("Failed to authenticate with Tableau")
            
            logger.info("Data source connections initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize data sources: {str(e)}")
            raise
    
    def extract_data(self) -> Dict[str, Any]:
        """Extract data from all configured sources"""
        logger.info("Starting data extraction...")
        extracted_data = {}
        
        try:
            # Extract from Oracle
            if 'oracle' in self.data_sources:
                logger.info("Extracting data from Oracle...")
                oracle_data = {
                    'students': self.data_sources['oracle'].extract_students(),
                    'courses': self.data_sources['oracle'].extract_courses(),
                    'enrollments': self.data_sources['oracle'].extract_enrollments(),
                    'academic_records': self.data_sources['oracle'].extract_academic_records()
                }
                extracted_data['oracle'] = oracle_data
                logger.info(f"Oracle extraction completed: {sum(len(df) for df in oracle_data.values())} total records")
            
            # Extract from Workday
            if 'workday' in self.data_sources:
                logger.info("Extracting data from Workday...")
                workday_data = {
                    'students': self.data_sources['workday'].get_students(),
                    'academic_programs': self.data_sources['workday'].get_academic_programs(),
                    'job_postings': self.data_sources['workday'].get_job_postings()
                }
                extracted_data['workday'] = workday_data
                logger.info(f"Workday extraction completed: {sum(len(df) for df in workday_data.values())} total records")
            
            # Extract from Tableau
            if 'tableau' in self.data_sources:
                logger.info("Extracting data from Tableau...")
                tableau_data = {
                    'student_analytics': self.data_sources['tableau'].get_student_analytics(),
                    'job_market_trends': self.data_sources['tableau'].get_job_market_trends()
                }
                extracted_data['tableau'] = tableau_data
                logger.info(f"Tableau extraction completed: {sum(len(df) for df in tableau_data.values())} total records")
            
            # Send extraction metrics
            total_records = sum(
                sum(len(df) for df in source_data.values()) 
                for source_data in extracted_data.values()
            )
            self.monitoring.send_custom_metrics({
                'RecordsExtracted': total_records,
                'DataSourcesProcessed': len(extracted_data)
            })
            
            logger.info(f"Data extraction completed: {total_records} total records from {len(extracted_data)} sources")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")
            raise
    
    def transform_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform and clean extracted data"""
        logger.info("Starting data transformation...")
        
        try:
            transformer = DataTransformer()
            transformed_data = {}
            
            # Transform Oracle data
            if 'oracle' in extracted_data:
                oracle_transformed = transformer.transform_oracle_data(extracted_data['oracle'])
                transformed_data['oracle'] = oracle_transformed
            
            # Transform Workday data
            if 'workday' in extracted_data:
                workday_transformed = transformer.transform_workday_data(extracted_data['workday'])
                transformed_data['workday'] = workday_transformed
            
            # Transform Tableau data
            if 'tableau' in extracted_data:
                tableau_transformed = transformer.transform_tableau_data(extracted_data['tableau'])
                transformed_data['tableau'] = tableau_transformed
            
            # Create unified datasets
            unified_data = transformer.create_unified_datasets(transformed_data)
            transformed_data['unified'] = unified_data
            
            # Send transformation metrics
            total_transformed = sum(
                sum(len(df) for df in source_data.values()) 
                for source_data in transformed_data.values()
            )
            self.monitoring.send_custom_metrics({
                'RecordsTransformed': total_transformed,
                'TransformationSuccess': 1
            })
            
            logger.info(f"Data transformation completed: {total_transformed} records processed")
            return transformed_data
            
        except Exception as e:
            logger.error(f"Data transformation failed: {str(e)}")
            raise
    
    def load_data(self, transformed_data: Dict[str, Any]) -> bool:
        """Load transformed data to S3"""
        logger.info("Starting data loading to S3...")
        
        try:
            bucket_name = self.config['s3']['data_lake_bucket'].format(
                account_id=self.config['aws']['account_id']
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Load each dataset to S3
            for source_name, source_data in transformed_data.items():
                for dataset_name, dataset in source_data.items():
                    if hasattr(dataset, 'to_parquet'):  # Check if it's a DataFrame
                        s3_key = f"processed/{source_name}/{dataset_name}/{timestamp}/data.parquet"
                        
                        # Convert DataFrame to parquet and upload
                        parquet_buffer = dataset.to_parquet()
                        self.s3_client.put_object(
                            Bucket=bucket_name,
                            Key=s3_key,
                            Body=parquet_buffer,
                            ContentType='application/octet-stream'
                        )
                        logger.info(f"Loaded {dataset_name} to s3://{bucket_name}/{s3_key}")
            
            # Create search index
            self.create_search_index(transformed_data, bucket_name, timestamp)
            
            # Send loading metrics
            self.monitoring.send_custom_metrics({
                'DataLoadSuccess': 1,
                'S3ObjectsCreated': len(transformed_data) * 2  # Approximate
            })
            
            logger.info("Data loading completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Data loading failed: {str(e)}")
            raise
    
    def create_search_index(self, transformed_data: Dict[str, Any], bucket_name: str, timestamp: str):
        """Create search index for Lambda function"""
        logger.info("Creating search index...")
        
        try:
            # Combine all relevant data for search
            search_records = []
            
            # Add student profiles
            if 'unified' in transformed_data and 'student_profiles' in transformed_data['unified']:
                student_profiles = transformed_data['unified']['student_profiles']
                for _, row in student_profiles.iterrows():
                    search_records.append({
                        'student_id': row.get('student_id'),
                        'academic_program': row.get('academic_program'),
                        'gpa': row.get('gpa'),
                        'performance_score': row.get('performance_score'),
                        'career_interest': row.get('career_interest'),
                        'skill_gaps': row.get('skill_gaps', []),
                        'recommended_courses': row.get('recommended_courses', []),
                        'data_source': 'unified',
                        'record_type': 'student_profile'
                    })
            
            # Add job postings
            if 'workday' in transformed_data and 'job_postings' in transformed_data['workday']:
                job_postings = transformed_data['workday']['job_postings']
                for _, row in job_postings.iterrows():
                    search_records.append({
                        'job_posting_id': row.get('job_posting_id'),
                        'job_title': row.get('job_title'),
                        'company': row.get('company'),
                        'location': row.get('location'),
                        'required_skills': row.get('required_skills', []),
                        'salary_range': row.get('salary_range'),
                        'data_source': 'workday',
                        'record_type': 'job_posting'
                    })
            
            # Create search index JSON
            search_index = {
                'index_created_at': datetime.now().isoformat(),
                'total_records': len(search_records),
                'records': search_records
            }
            
            # Upload search index to S3
            s3_key = f"search-index/student-resources.json"
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=json.dumps(search_index, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Search index created with {len(search_records)} records")
            
        except Exception as e:
            logger.error(f"Failed to create search index: {str(e)}")
            raise
    
    def cleanup_connections(self):
        """Clean up data source connections"""
        logger.info("Cleaning up connections...")
        
        for source_name, connector in self.data_sources.items():
            try:
                if hasattr(connector, 'disconnect'):
                    connector.disconnect()
                elif hasattr(connector, 'close'):
                    connector.close()
                logger.info(f"Closed connection to {source_name}")
            except Exception as e:
                logger.warning(f"Failed to close connection to {source_name}: {str(e)}")
    
    def run_pipeline(self) -> bool:
        """Run the complete ETL pipeline"""
        start_time = datetime.now()
        logger.info("Starting Ed-Tech ETL Pipeline...")
        
        try:
            # Initialize data sources
            self.initialize_data_sources()
            
            # Extract data
            extracted_data = self.extract_data()
            
            # Transform data
            transformed_data = self.transform_data(extracted_data)
            
            # Load data
            success = self.load_data(transformed_data)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Send completion metrics
            self.monitoring.send_custom_metrics({
                'PipelineExecutionTime': processing_time,
                'PipelineSuccess': 1 if success else 0
            })
            
            logger.info(f"ETL Pipeline completed successfully in {processing_time:.2f} seconds")
            return success
            
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {str(e)}")
            self.monitoring.send_custom_metrics({
                'PipelineSuccess': 0,
                'PipelineErrors': 1
            })
            return False
            
        finally:
            # Always cleanup connections
            self.cleanup_connections()

def main():
    """Main function to run the ETL pipeline"""
    try:
        pipeline = EdTechETLPipeline()
        success = pipeline.run_pipeline()
        
        if success:
            print("ETL Pipeline completed successfully!")
            sys.exit(0)
        else:
            print("ETL Pipeline failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"ETL Pipeline error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
