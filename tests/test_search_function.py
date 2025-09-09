"""
Test suite for the Ed-Tech Search Lambda Function
"""

import json
import pytest
import boto3
from moto import mock_s3, mock_cloudwatch
from unittest.mock import patch, MagicMock
import sys
import os

# Add lambda directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from search_handler import lambda_handler, EdTechSearchEngine

class TestEdTechSearchFunction:
    """Test cases for the search Lambda function"""
    
    @pytest.fixture
    def sample_search_index(self):
        """Sample search index data for testing"""
        return {
            "index_created_at": "2024-01-15T10:00:00Z",
            "total_records": 3,
            "records": [
                {
                    "student_id": "STU001",
                    "academic_program": "Computer Science",
                    "gpa": 3.8,
                    "performance_score": 85.5,
                    "career_interest": "Software Engineering",
                    "skill_gaps": ["Machine Learning", "System Design"],
                    "recommended_courses": ["ML101", "CS201"],
                    "record_type": "student_profile"
                },
                {
                    "job_posting_id": "JOB001",
                    "job_title": "Software Engineer",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "required_skills": ["Python", "AWS", "Docker"],
                    "salary_range": "80k-120k",
                    "record_type": "job_posting"
                },
                {
                    "student_id": "STU002",
                    "academic_program": "Data Science",
                    "gpa": 3.6,
                    "performance_score": 92.0,
                    "career_interest": "Data Science",
                    "skill_gaps": ["Deep Learning", "Statistics"],
                    "recommended_courses": ["DL101", "STAT201"],
                    "record_type": "student_profile"
                }
            ]
        }
    
    @mock_s3
    @mock_cloudwatch
    def test_search_students(self, sample_search_index):
        """Test student search functionality"""
        # Mock S3 response
        with patch('search_handler.s3_client') as mock_s3:
            mock_s3.get_object.return_value = {
                'Body': MagicMock(read=lambda: json.dumps(sample_search_index).encode())
            }
            
            # Test search event
            event = {
                "action": "search_students",
                "query": "Computer Science",
                "filters": {}
            }
            
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['action'] == 'search_students'
            assert body['query'] == 'Computer Science'
            assert len(body['results']) > 0
            
            # Check that results contain Computer Science students
            computer_science_students = [
                result for result in body['results'] 
                if 'Computer Science' in result.get('academic_program', '')
            ]
            assert len(computer_science_students) > 0
    
    @mock_s3
    @mock_cloudwatch
    def test_search_jobs(self, sample_search_index):
        """Test job search functionality"""
        with patch('search_handler.s3_client') as mock_s3:
            mock_s3.get_object.return_value = {
                'Body': MagicMock(read=lambda: json.dumps(sample_search_index).encode())
            }
            
            event = {
                "action": "search_jobs",
                "query": "Software Engineer",
                "filters": {}
            }
            
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['action'] == 'search_jobs'
            assert len(body['results']) > 0
            
            # Check that results contain Software Engineer jobs
            software_jobs = [
                result for result in body['results'] 
                if 'Software Engineer' in result.get('job_title', '')
            ]
            assert len(software_jobs) > 0
    
    @mock_s3
    @mock_cloudwatch
    def test_get_recommendations(self, sample_search_index):
        """Test personalized recommendations"""
        with patch('search_handler.s3_client') as mock_s3:
            mock_s3.get_object.return_value = {
                'Body': MagicMock(read=lambda: json.dumps(sample_search_index).encode())
            }
            
            event = {
                "action": "get_recommendations",
                "student_id": "STU001"
            }
            
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'jobs' in body
            assert 'courses' in body
            assert isinstance(body['jobs'], list)
            assert isinstance(body['courses'], list)
    
    @mock_s3
    @mock_cloudwatch
    def test_search_with_filters(self, sample_search_index):
        """Test search with filters"""
        with patch('search_handler.s3_client') as mock_s3:
            mock_s3.get_object.return_value = {
                'Body': MagicMock(read=lambda: json.dumps(sample_search_index).encode())
            }
            
            event = {
                "action": "search_students",
                "query": "Science",
                "filters": {
                    "min_gpa": 3.5
                }
            }
            
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            
            # Check that all results meet the GPA filter
            for result in body['results']:
                if 'gpa' in result and result['gpa'] is not None:
                    assert result['gpa'] >= 3.5
    
    @mock_s3
    @mock_cloudwatch
    def test_invalid_action(self, sample_search_index):
        """Test invalid action handling"""
        with patch('search_handler.s3_client') as mock_s3:
            mock_s3.get_object.return_value = {
                'Body': MagicMock(read=lambda: json.dumps(sample_search_index).encode())
            }
            
            event = {
                "action": "invalid_action",
                "query": "test"
            }
            
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 400
            body = json.loads(response['body'])
            assert 'error' in body
    
    @mock_s3
    @mock_cloudwatch
    def test_missing_student_id_for_recommendations(self, sample_search_index):
        """Test recommendations without student_id"""
        with patch('search_handler.s3_client') as mock_s3:
            mock_s3.get_object.return_value = {
                'Body': MagicMock(read=lambda: json.dumps(sample_search_index).encode())
            }
            
            event = {
                "action": "get_recommendations"
            }
            
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 400
            body = json.loads(response['body'])
            assert 'student_id is required' in body['error']
    
    @mock_s3
    @mock_cloudwatch
    def test_empty_search_index(self):
        """Test handling of empty search index"""
        empty_index = {"records": []}
        
        with patch('search_handler.s3_client') as mock_s3:
            mock_s3.get_object.return_value = {
                'Body': MagicMock(read=lambda: json.dumps(empty_index).encode())
            }
            
            event = {
                "action": "search_students",
                "query": "test"
            }
            
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert len(body['results']) == 0
    
    @mock_s3
    @mock_cloudwatch
    def test_s3_error_handling(self):
        """Test S3 error handling"""
        with patch('search_handler.s3_client') as mock_s3:
            mock_s3.get_object.side_effect = Exception("S3 Error")
            
            event = {
                "action": "search_students",
                "query": "test"
            }
            
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert len(body['results']) == 0
    
    def test_search_engine_initialization(self):
        """Test search engine initialization"""
        with patch('search_handler.s3_client') as mock_s3:
            mock_s3.get_object.return_value = {
                'Body': MagicMock(read=lambda: json.dumps({"records": []}).encode())
            }
            
            search_engine = EdTechSearchEngine()
            assert search_engine.search_index is not None
            assert 'records' in search_engine.search_index
    
    def test_relevance_score_calculation(self):
        """Test relevance score calculation"""
        with patch('search_handler.s3_client') as mock_s3:
            mock_s3.get_object.return_value = {
                'Body': MagicMock(read=lambda: json.dumps({"records": []}).encode())
            }
            
            search_engine = EdTechSearchEngine()
            
            # Test student relevance
            student_record = {
                'academic_program': 'Computer Science',
                'career_interest': 'Software Engineering',
                'skill_gaps': ['Python', 'AWS']
            }
            
            score = search_engine.calculate_relevance_score(student_record, 'computer science')
            assert score > 0
            
            # Test job relevance
            job_record = {
                'job_title': 'Software Engineer',
                'company': 'Tech Corp',
                'required_skills': ['Python', 'AWS']
            }
            
            score = search_engine.calculate_job_relevance_score(job_record, 'software engineer')
            assert score > 0

if __name__ == "__main__":
    pytest.main([__file__])
