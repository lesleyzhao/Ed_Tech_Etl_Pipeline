"""
Workday API Connector for Ed-Tech ETL Pipeline
Handles data extraction from Workday HCM system
"""

import requests
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import json
import base64

logger = logging.getLogger(__name__)

class WorkdayConnector:
    """Workday API connector for ETL pipeline"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config['base_url']
        self.tenant = config['tenant']
        self.username = config['username']
        self.password = config['password']
        self.session = requests.Session()
        self.access_token = None
    
    def authenticate(self) -> bool:
        """Authenticate with Workday API"""
        try:
            # Workday uses OAuth 2.0 for authentication
            auth_url = f"{self.base_url}/ccx/oauth2/{self.tenant}/token"
            
            # Create basic auth header
            credentials = f"{self.username}:{self.password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials',
                'scope': 'wd:read'
            }
            
            response = self.session.post(auth_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Set authorization header for future requests
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            
            logger.info("Successfully authenticated with Workday API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Workday: {str(e)}")
            return False
    
    def get_students(self, limit: int = 1000, offset: int = 0) -> pd.DataFrame:
        """Extract students data from Workday"""
        endpoint = f"{self.base_url}/ccx/api/v1/{self.tenant}/students"
        
        params = {
            'limit': limit,
            'offset': offset,
            'include': 'academic_program,contact_info,academic_records'
        }
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            students_data = []
            
            for student in data.get('students', []):
                student_record = {
                    'student_id': student.get('id'),
                    'first_name': student.get('first_name'),
                    'last_name': student.get('last_name'),
                    'email': student.get('email'),
                    'academic_program': student.get('academic_program', {}).get('name'),
                    'program_id': student.get('academic_program', {}).get('id'),
                    'enrollment_date': student.get('enrollment_date'),
                    'expected_graduation': student.get('expected_graduation'),
                    'status': student.get('status'),
                    'gpa': student.get('academic_records', {}).get('current_gpa'),
                    'total_credits': student.get('academic_records', {}).get('total_credits'),
                    'academic_standing': student.get('academic_records', {}).get('standing')
                }
                students_data.append(student_record)
            
            df = pd.DataFrame(students_data)
            logger.info(f"Extracted {len(df)} student records from Workday")
            return df
            
        except Exception as e:
            logger.error(f"Failed to extract students from Workday: {str(e)}")
            return pd.DataFrame()
    
    def get_academic_programs(self) -> pd.DataFrame:
        """Extract academic programs from Workday"""
        endpoint = f"{self.base_url}/ccx/api/v1/{self.tenant}/academic_programs"
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            data = response.json()
            programs_data = []
            
            for program in data.get('academic_programs', []):
                program_record = {
                    'program_id': program.get('id'),
                    'program_name': program.get('name'),
                    'department': program.get('department'),
                    'degree_level': program.get('degree_level'),
                    'duration_years': program.get('duration_years'),
                    'total_credits': program.get('total_credits'),
                    'description': program.get('description'),
                    'status': program.get('status')
                }
                programs_data.append(program_record)
            
            df = pd.DataFrame(programs_data)
            logger.info(f"Extracted {len(df)} academic program records from Workday")
            return df
            
        except Exception as e:
            logger.error(f"Failed to extract academic programs from Workday: {str(e)}")
            return pd.DataFrame()
    
    def get_job_postings(self, limit: int = 1000, offset: int = 0) -> pd.DataFrame:
        """Extract job postings from Workday"""
        endpoint = f"{self.base_url}/ccx/api/v1/{self.tenant}/job_postings"
        
        params = {
            'limit': limit,
            'offset': offset,
            'include': 'job_requirements,compensation,location',
            'status': 'ACTIVE'
        }
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            jobs_data = []
            
            for job in data.get('job_postings', []):
                job_record = {
                    'job_posting_id': job.get('id'),
                    'job_title': job.get('title'),
                    'company': job.get('company', {}).get('name'),
                    'location': job.get('location', {}).get('city') + ', ' + job.get('location', {}).get('state'),
                    'department': job.get('department'),
                    'job_type': job.get('job_type'),
                    'employment_type': job.get('employment_type'),
                    'required_skills': [skill.get('name') for skill in job.get('required_skills', [])],
                    'preferred_skills': [skill.get('name') for skill in job.get('preferred_skills', [])],
                    'education_requirements': job.get('education_requirements'),
                    'experience_requirements': job.get('experience_requirements'),
                    'salary_min': job.get('compensation', {}).get('salary_min'),
                    'salary_max': job.get('compensation', {}).get('salary_max'),
                    'salary_currency': job.get('compensation', {}).get('currency'),
                    'posting_date': job.get('posting_date'),
                    'application_deadline': job.get('application_deadline'),
                    'description': job.get('description'),
                    'status': job.get('status')
                }
                jobs_data.append(job_record)
            
            df = pd.DataFrame(jobs_data)
            logger.info(f"Extracted {len(df)} job posting records from Workday")
            return df
            
        except Exception as e:
            logger.error(f"Failed to extract job postings from Workday: {str(e)}")
            return pd.DataFrame()
    
    def get_student_job_matches(self, student_id: str) -> pd.DataFrame:
        """Get job matches for a specific student based on their profile"""
        # This would typically involve ML-based matching
        # For prototype, we'll return sample matches
        endpoint = f"{self.base_url}/ccx/api/v1/{self.tenant}/students/{student_id}/job_matches"
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            data = response.json()
            matches_data = []
            
            for match in data.get('job_matches', []):
                match_record = {
                    'student_id': student_id,
                    'job_posting_id': match.get('job_posting_id'),
                    'match_score': match.get('match_score'),
                    'match_reasons': match.get('match_reasons', []),
                    'created_at': match.get('created_at')
                }
                matches_data.append(match_record)
            
            df = pd.DataFrame(matches_data)
            logger.info(f"Extracted {len(df)} job match records for student {student_id}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to extract job matches for student {student_id}: {str(e)}")
            return pd.DataFrame()
    
    def get_data_quality_metrics(self) -> Dict[str, Any]:
        """Get data quality metrics from Workday"""
        try:
            # Get basic counts
            students_count = self.get_students(limit=1).shape[0]
            programs_count = self.get_academic_programs().shape[0]
            jobs_count = self.get_job_postings(limit=1).shape[0]
            
            return {
                'total_students': students_count,
                'total_programs': programs_count,
                'total_job_postings': jobs_count,
                'last_updated': datetime.now().isoformat(),
                'data_freshness': 'real_time'
            }
            
        except Exception as e:
            logger.error(f"Failed to get data quality metrics: {str(e)}")
            return {}
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()
            logger.info("Closed Workday API session")
