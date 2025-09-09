"""
Test suite for the Ed-Tech ETL Pipeline
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from etl.transformations.data_transformer import DataTransformer
from etl.data_sources.oracle_connector import OracleConnector
from etl.data_sources.workday_connector import WorkdayConnector
from etl.data_sources.tableau_connector import TableauConnector

class TestDataTransformer:
    """Test cases for data transformation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.transformer = DataTransformer()
    
    def test_clean_text_data(self):
        """Test text data cleaning"""
        # Test normal text
        assert self.transformer.clean_text_data("  Hello World  ") == "Hello World"
        
        # Test text with special characters
        assert self.transformer.clean_text_data("Hello@World#123") == "HelloWorld123"
        
        # Test None and NaN values
        assert self.transformer.clean_text_data(None) == ""
        assert self.transformer.clean_text_data(np.nan) == ""
    
    def test_validate_email(self):
        """Test email validation"""
        # Valid emails
        assert self.transformer.validate_email("test@example.com") == True
        assert self.transformer.validate_email("user.name@domain.co.uk") == True
        
        # Invalid emails
        assert self.transformer.validate_email("invalid-email") == False
        assert self.transformer.validate_email("@example.com") == False
        assert self.transformer.validate_email("test@") == False
        assert self.transformer.validate_email(None) == False
    
    def test_validate_student_id(self):
        """Test student ID validation"""
        # Valid student IDs
        assert self.transformer.validate_student_id("STU001") == True
        assert self.transformer.validate_student_id("STU999") == True
        
        # Invalid student IDs
        assert self.transformer.validate_student_id("stu001") == False
        assert self.transformer.validate_student_id("STU01") == False
        assert self.transformer.validate_student_id("STU0001") == False
        assert self.transformer.validate_student_id("STU") == False
        assert self.transformer.validate_student_id(None) == False
    
    def test_clean_gpa(self):
        """Test GPA cleaning and validation"""
        # Valid GPAs
        assert self.transformer.clean_gpa(3.5) == 3.5
        assert self.transformer.clean_gpa("3.7") == 3.7
        assert self.transformer.clean_gpa(4.0) == 4.0
        
        # Invalid GPAs
        assert self.transformer.clean_gpa(5.0) is None
        assert self.transformer.clean_gpa(-1.0) is None
        assert self.transformer.clean_gpa("invalid") is None
        assert self.transformer.clean_gpa(None) is None
    
    def test_transform_students_table(self):
        """Test students table transformation"""
        # Create sample data
        data = {
            'student_id': ['STU001', 'STU002', 'invalid_id'],
            'first_name': ['John', 'Jane', 'Bob'],
            'last_name': ['Doe', 'Smith', 'Johnson'],
            'email': ['john@example.com', 'jane@example.com', 'invalid-email'],
            'gpa': [3.5, 3.8, 5.0],  # 5.0 is invalid
            'academic_program': ['computer science', 'data science', 'business administration']
        }
        df = pd.DataFrame(data)
        
        # Transform data
        transformed_df = self.transformer._transform_students_table(df)
        
        # Check transformations
        assert len(transformed_df) == 3
        assert 'full_name' in transformed_df.columns
        assert transformed_df['full_name'].iloc[0] == 'John Doe'
        assert transformed_df['academic_program'].iloc[0] == 'Computer Science'
        assert transformed_df['gpa'].iloc[2] is None  # Invalid GPA should be None
    
    def test_clean_salary_range(self):
        """Test salary range cleaning"""
        # Test various salary formats
        assert self.transformer._clean_salary_range("$80,000 - $120,000") == "80000-120000"
        assert self.transformer._clean_salary_range("80k-120k") == "80-120"
        assert self.transformer._clean_salary_range("100000") == "100000"
        assert self.transformer._clean_salary_range(None) == ""
    
    def test_clean_skills_list(self):
        """Test skills list cleaning"""
        # Test list input
        skills_list = ["Python", "AWS", "Docker"]
        assert self.transformer._clean_skills_list(skills_list) == skills_list
        
        # Test string input
        skills_string = "Python, AWS, Docker"
        result = self.transformer._clean_skills_list(skills_string)
        assert "Python" in result
        assert "AWS" in result
        assert "Docker" in result
        
        # Test None input
        assert self.transformer._clean_skills_list(None) == []
    
    def test_calculate_data_quality_score(self):
        """Test data quality score calculation"""
        # Perfect data
        perfect_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        score = self.transformer._calculate_data_quality_score(perfect_df, 'test')
        assert score == 1.0
        
        # Data with nulls
        null_df = pd.DataFrame({
            'col1': [1, None, 3],
            'col2': ['a', 'b', None]
        })
        score = self.transformer._calculate_data_quality_score(null_df, 'test')
        assert 0 < score < 1
        
        # Empty dataframe
        empty_df = pd.DataFrame()
        score = self.transformer._calculate_data_quality_score(empty_df, 'test')
        assert score == 0.0

class TestOracleConnector:
    """Test cases for Oracle connector"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = {
            'host': 'test-host',
            'port': 1521,
            'service_name': 'TEST',
            'username': 'test_user',
            'password': 'test_password'
        }
        self.connector = OracleConnector(self.config)
    
    @patch('etl.data_sources.oracle_connector.cx_Oracle')
    def test_connect_success(self, mock_cx_oracle):
        """Test successful connection"""
        mock_connection = MagicMock()
        mock_cx_oracle.connect.return_value = mock_connection
        
        result = self.connector.connect()
        assert result == True
        assert self.connector.connection == mock_connection
    
    @patch('etl.data_sources.oracle_connector.cx_Oracle')
    def test_connect_failure(self, mock_cx_oracle):
        """Test connection failure"""
        mock_cx_oracle.connect.side_effect = Exception("Connection failed")
        
        result = self.connector.connect()
        assert result == False
        assert self.connector.connection is None
    
    @patch('etl.data_sources.oracle_connector.pd.read_sql')
    def test_extract_students(self, mock_read_sql):
        """Test students data extraction"""
        # Mock connection
        self.connector.connection = MagicMock()
        
        # Mock pandas response
        mock_df = pd.DataFrame({
            'student_id': ['STU001', 'STU002'],
            'first_name': ['John', 'Jane'],
            'last_name': ['Doe', 'Smith']
        })
        mock_read_sql.return_value = mock_df
        
        result = self.connector.extract_students()
        
        assert len(result) == 2
        assert 'student_id' in result.columns
        mock_read_sql.assert_called_once()

class TestWorkdayConnector:
    """Test cases for Workday connector"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = {
            'base_url': 'https://test.workday.com',
            'tenant': 'test_tenant',
            'username': 'test_user',
            'password': 'test_password'
        }
        self.connector = WorkdayConnector(self.config)
    
    @patch('etl.data_sources.workday_connector.requests.Session.post')
    def test_authenticate_success(self, mock_post):
        """Test successful authentication"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'access_token': 'test_token'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.connector.authenticate()
        assert result == True
        assert self.connector.access_token == 'test_token'
    
    @patch('etl.data_sources.workday_connector.requests.Session.post')
    def test_authenticate_failure(self, mock_post):
        """Test authentication failure"""
        mock_post.side_effect = Exception("Auth failed")
        
        result = self.connector.authenticate()
        assert result == False
        assert self.connector.access_token is None

class TestTableauConnector:
    """Test cases for Tableau connector"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = {
            'server_url': 'https://test.tableau.com',
            'site_id': 'test_site',
            'username': 'test_user',
            'password': 'test_password'
        }
        self.connector = TableauConnector(self.config)
    
    def test_get_student_analytics(self):
        """Test student analytics data extraction"""
        result = self.connector.get_student_analytics()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'student_id' in result.columns
        assert 'performance_score' in result.columns
    
    def test_get_job_market_trends(self):
        """Test job market trends data extraction"""
        result = self.connector.get_job_market_trends()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'skill' in result.columns
        assert 'demand_score' in result.columns

class TestETLPipelineIntegration:
    """Integration tests for ETL pipeline"""
    
    @patch('etl.run_pipeline.boto3.client')
    @patch('etl.run_pipeline.CloudWatchMonitoring')
    def test_pipeline_initialization(self, mock_monitoring, mock_boto3):
        """Test pipeline initialization"""
        from etl.run_pipeline import EdTechETLPipeline
        
        # Mock configuration
        mock_config = {
            'aws': {'account_id': '123456789012'},
            's3': {'data_lake_bucket': 'test-bucket-{account_id}'},
            'data_sources': {}
        }
        
        with patch('etl.run_pipeline.EdTechETLPipeline.load_config', return_value=mock_config):
            pipeline = EdTechETLPipeline()
            assert pipeline.config == mock_config
            assert pipeline.s3_client is not None
            assert pipeline.monitoring is not None

if __name__ == "__main__":
    pytest.main([__file__])
