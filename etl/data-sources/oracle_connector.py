"""
Oracle Database Connector for Ed-Tech ETL Pipeline
Handles data extraction from Oracle database
"""

import cx_Oracle
import pandas as pd
from typing import Dict, List, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class OracleConnector:
    """Oracle database connector for ETL pipeline"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
    
    def connect(self):
        """Establish connection to Oracle database"""
        try:
            dsn = cx_Oracle.makedsn(
                self.config['host'],
                self.config['port'],
                service_name=self.config['service_name']
            )
            
            self.connection = cx_Oracle.connect(
                self.config['username'],
                self.config['password'],
                dsn
            )
            
            logger.info("Successfully connected to Oracle database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Oracle: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from Oracle database")
    
    def extract_students(self) -> pd.DataFrame:
        """Extract students data from Oracle"""
        query = """
        SELECT 
            student_id,
            first_name,
            last_name,
            email,
            academic_program,
            enrollment_date,
            graduation_date,
            gpa,
            status
        FROM students 
        WHERE status = 'ACTIVE'
        """
        
        try:
            df = pd.read_sql(query, self.connection)
            logger.info(f"Extracted {len(df)} student records from Oracle")
            return df
        except Exception as e:
            logger.error(f"Failed to extract students: {str(e)}")
            return pd.DataFrame()
    
    def extract_courses(self) -> pd.DataFrame:
        """Extract courses data from Oracle"""
        query = """
        SELECT 
            course_id,
            course_name,
            course_code,
            department,
            credits,
            description,
            prerequisites
        FROM courses
        WHERE status = 'ACTIVE'
        """
        
        try:
            df = pd.read_sql(query, self.connection)
            logger.info(f"Extracted {len(df)} course records from Oracle")
            return df
        except Exception as e:
            logger.error(f"Failed to extract courses: {str(e)}")
            return pd.DataFrame()
    
    def extract_enrollments(self) -> pd.DataFrame:
        """Extract enrollment data from Oracle"""
        query = """
        SELECT 
            enrollment_id,
            student_id,
            course_id,
            semester,
            year,
            grade,
            enrollment_date,
            status
        FROM enrollments
        WHERE status = 'ENROLLED'
        """
        
        try:
            df = pd.read_sql(query, self.connection)
            logger.info(f"Extracted {len(df)} enrollment records from Oracle")
            return df
        except Exception as e:
            logger.error(f"Failed to extract enrollments: {str(e)}")
            return pd.DataFrame()
    
    def extract_academic_records(self) -> pd.DataFrame:
        """Extract academic records from Oracle"""
        query = """
        SELECT 
            record_id,
            student_id,
            semester,
            year,
            total_credits,
            gpa,
            academic_standing,
            honors
        FROM academic_records
        ORDER BY year DESC, semester DESC
        """
        
        try:
            df = pd.read_sql(query, self.connection)
            logger.info(f"Extracted {len(df)} academic record entries from Oracle")
            return df
        except Exception as e:
            logger.error(f"Failed to extract academic records: {str(e)}")
            return pd.DataFrame()
    
    def get_table_metadata(self, table_name: str) -> Dict[str, Any]:
        """Get table metadata for schema validation"""
        query = """
        SELECT 
            column_name,
            data_type,
            data_length,
            nullable,
            data_default
        FROM user_tab_columns 
        WHERE table_name = UPPER(:table_name)
        ORDER BY column_id
        """
        
        try:
            df = pd.read_sql(query, self.connection, params={'table_name': table_name})
            return {
                'table_name': table_name,
                'columns': df.to_dict('records'),
                'extracted_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get metadata for table {table_name}: {str(e)}")
            return {}
    
    def validate_data_quality(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """Validate data quality for extracted data"""
        validation_results = {
            'table_name': table_name,
            'total_records': len(df),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_records': df.duplicated().sum(),
            'validation_timestamp': datetime.now().isoformat()
        }
        
        # Check for required fields based on table
        if table_name == 'students':
            required_fields = ['student_id', 'first_name', 'last_name', 'email']
            for field in required_fields:
                if field in df.columns:
                    validation_results[f'{field}_completeness'] = (1 - df[field].isnull().sum() / len(df)) * 100
        
        return validation_results
