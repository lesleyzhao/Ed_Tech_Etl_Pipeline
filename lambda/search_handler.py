"""
AWS Lambda Search Function for Ed-Tech Platform
Provides fast search and recommendation capabilities
"""

import json
import boto3
import os
from typing import Dict, List, Any
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')

# Environment variables
S3_BUCKET = os.environ.get('S3_BUCKET', 'ed-tech-data-lake-123456789012')
SEARCH_INDEX_KEY = os.environ.get('SEARCH_INDEX_KEY', 'search-index/student-resources.json')

class EdTechSearchEngine:
    """Search engine for student resources and job recommendations"""
    
    def __init__(self):
        self.search_index = None
        self.load_search_index()
    
    def load_search_index(self):
        """Load search index from S3"""
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=SEARCH_INDEX_KEY)
            self.search_index = json.loads(response['Body'].read().decode('utf-8'))
            logger.info(f"Loaded search index with {self.search_index.get('total_records', 0)} records")
        except Exception as e:
            logger.error(f"Failed to load search index: {str(e)}")
            self.search_index = {"records": []}
    
    def search_students(self, query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        """Search for students based on query and filters"""
        if not self.search_index or not self.search_index.get('records'):
            return []
        
        results = []
        query_lower = query.lower()
        
        for record in self.search_index['records']:
            score = self.calculate_relevance_score(record, query_lower, filters)
            if score > 0:
                results.append({
                    'student_id': record.get('student_id'),
                    'academic_program': record.get('academic_program'),
                    'gpa': record.get('gpa'),
                    'performance_score': record.get('performance_score'),
                    'career_interest': record.get('career_interest'),
                    'skills': record.get('skill_gaps', []),
                    'relevance_score': score
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:50]  # Limit to top 50 results
    
    def search_jobs(self, query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        """Search for job postings based on query and filters"""
        if not self.search_index or not self.search_index.get('records'):
            return []
        
        results = []
        query_lower = query.lower()
        
        for record in self.search_index['records']:
            if not record.get('job_title'):
                continue
                
            score = self.calculate_job_relevance_score(record, query_lower, filters)
            if score > 0:
                results.append({
                    'job_posting_id': record.get('job_posting_id'),
                    'job_title': record.get('job_title'),
                    'company': record.get('company'),
                    'location': record.get('location'),
                    'required_skills': record.get('required_skills', []),
                    'salary_range': record.get('salary_range'),
                    'match_score': record.get('match_score', 0),
                    'relevance_score': score
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:50]  # Limit to top 50 results
    
    def get_recommendations(self, student_id: str) -> Dict[str, List[Dict]]:
        """Get personalized recommendations for a student"""
        if not self.search_index or not self.search_index.get('records'):
            return {"jobs": [], "courses": []}
        
        # Find student record
        student_record = None
        for record in self.search_index['records']:
            if record.get('student_id') == student_id:
                student_record = record
                break
        
        if not student_record:
            return {"jobs": [], "courses": []}
        
        # Get job recommendations based on student profile
        job_recommendations = []
        for record in self.search_index['records']:
            if record.get('student_id') == student_id and record.get('job_title'):
                job_recommendations.append({
                    'job_title': record.get('job_title'),
                    'company': record.get('company'),
                    'location': record.get('location'),
                    'required_skills': record.get('required_skills', []),
                    'salary_range': record.get('salary_range'),
                    'match_score': record.get('match_score', 0)
                })
        
        # Get course recommendations
        course_recommendations = []
        recommended_courses = student_record.get('recommended_courses', [])
        for course in recommended_courses:
            course_recommendations.append({
                'course_id': course,
                'course_name': f"Course {course}",
                'reason': "Based on your skill gaps and career interests"
            })
        
        return {
            "jobs": job_recommendations[:10],
            "courses": course_recommendations[:5]
        }
    
    def calculate_relevance_score(self, record: Dict, query: str, filters: Dict = None) -> float:
        """Calculate relevance score for student search"""
        score = 0.0
        
        # Text matching
        text_fields = [
            record.get('academic_program', ''),
            record.get('career_interest', ''),
            ' '.join(record.get('skill_gaps', [])),
            ' '.join(record.get('recommended_courses', []))
        ]
        
        for field in text_fields:
            if query in field.lower():
                score += 1.0
        
        # Apply filters
        if filters:
            if 'academic_program' in filters:
                if record.get('academic_program', '').lower() != filters['academic_program'].lower():
                    return 0.0
            
            if 'min_gpa' in filters:
                if record.get('gpa', 0) < filters['min_gpa']:
                    return 0.0
        
        return score
    
    def calculate_job_relevance_score(self, record: Dict, query: str, filters: Dict = None) -> float:
        """Calculate relevance score for job search"""
        score = 0.0
        
        # Text matching
        text_fields = [
            record.get('job_title', ''),
            record.get('company', ''),
            record.get('location', ''),
            ' '.join(record.get('required_skills', []))
        ]
        
        for field in text_fields:
            if query in field.lower():
                score += 1.0
        
        # Apply filters
        if filters:
            if 'location' in filters:
                if filters['location'].lower() not in record.get('location', '').lower():
                    return 0.0
            
            if 'min_salary' in filters:
                salary_range = record.get('salary_range', '')
                # Simple salary parsing (in production, use more sophisticated parsing)
                if 'k' in salary_range.lower():
                    try:
                        min_salary = int(salary_range.split('-')[0].replace('k', '')) * 1000
                        if min_salary < filters['min_salary']:
                            return 0.0
                    except:
                        pass
        
        return score

# Initialize search engine
search_engine = EdTechSearchEngine()

def lambda_handler(event, context):
    """
    AWS Lambda handler for search requests
    
    Expected event format:
    {
        "action": "search_students" | "search_jobs" | "get_recommendations",
        "query": "search query string",
        "filters": {
            "academic_program": "Computer Science",
            "location": "San Francisco",
            "min_gpa": 3.5
        },
        "student_id": "STU001"  # for recommendations
    }
    """
    try:
        # Parse request
        action = event.get('action', 'search_students')
        query = event.get('query', '')
        filters = event.get('filters', {})
        student_id = event.get('student_id')
        
        # Log request for monitoring
        logger.info(f"Search request: action={action}, query={query}, filters={filters}")
        
        # Execute search based on action
        if action == 'search_students':
            results = search_engine.search_students(query, filters)
        elif action == 'search_jobs':
            results = search_engine.search_jobs(query, filters)
        elif action == 'get_recommendations':
            if not student_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'student_id is required for recommendations'})
                }
            results = search_engine.get_recommendations(student_id)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Invalid action: {action}'})
            }
        
        # Send custom metrics to CloudWatch
        cloudwatch.put_metric_data(
            Namespace='EdTech/Search',
            MetricData=[
                {
                    'MetricName': 'SearchRequests',
                    'Value': 1,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'SearchResults',
                    'Value': len(results) if isinstance(results, list) else 0,
                    'Unit': 'Count'
                }
            ]
        )
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'action': action,
                'query': query,
                'results': results,
                'total_results': len(results) if isinstance(results, list) else 0,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Search function error: {str(e)}")
        
        # Send error metric to CloudWatch
        cloudwatch.put_metric_data(
            Namespace='EdTech/Search',
            MetricData=[
                {
                    'MetricName': 'SearchErrors',
                    'Value': 1,
                    'Unit': 'Count'
                }
            ]
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
