"""
Tableau Server API Connector for Ed-Tech ETL Pipeline
Handles data extraction from Tableau workbooks and dashboards
"""

import requests
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class TableauConnector:
    """Tableau Server API connector for ETL pipeline"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.server_url = config['server_url']
        self.site_id = config['site_id']
        self.username = config['username']
        self.password = config['password']
        self.session = requests.Session()
        self.token = None
        self.site_luid = None
    
    def authenticate(self) -> bool:
        """Authenticate with Tableau Server"""
        try:
            # Tableau Server uses XML-based authentication
            auth_url = f"{self.server_url}/api/3.19/auth/signin"
            
            # Create XML request body
            xml_request = f"""
            <tsRequest>
                <credentials name="{self.username}" password="{self.password}">
                    <site contentUrl="{self.site_id}" />
                </credentials>
            </tsRequest>
            """
            
            headers = {
                'Content-Type': 'application/xml',
                'Accept': 'application/xml'
            }
            
            response = self.session.post(auth_url, data=xml_request, headers=headers)
            response.raise_for_status()
            
            # Parse response to get token and site LUID
            root = ET.fromstring(response.content)
            self.token = root.find('.//token').text
            self.site_luid = root.find('.//site').get('id')
            
            # Set headers for future requests
            self.session.headers.update({
                'X-Tableau-Auth': self.token,
                'Content-Type': 'application/xml',
                'Accept': 'application/xml'
            })
            
            logger.info("Successfully authenticated with Tableau Server")
            return True
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Tableau: {str(e)}")
            return False
    
    def get_workbooks(self) -> List[Dict[str, Any]]:
        """Get list of workbooks from Tableau Server"""
        endpoint = f"{self.server_url}/api/3.19/sites/{self.site_luid}/workbooks"
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            workbooks = []
            
            for workbook in root.findall('.//workbook'):
                workbook_info = {
                    'id': workbook.get('id'),
                    'name': workbook.get('name'),
                    'description': workbook.get('description'),
                    'created_at': workbook.get('createdAt'),
                    'updated_at': workbook.get('updatedAt'),
                    'size': workbook.get('size'),
                    'project_id': workbook.get('project', {}).get('id') if workbook.find('project') is not None else None
                }
                workbooks.append(workbook_info)
            
            logger.info(f"Retrieved {len(workbooks)} workbooks from Tableau")
            return workbooks
            
        except Exception as e:
            logger.error(f"Failed to get workbooks from Tableau: {str(e)}")
            return []
    
    def get_workbook_data(self, workbook_id: str, view_name: str) -> pd.DataFrame:
        """Extract data from a specific Tableau workbook view"""
        endpoint = f"{self.server_url}/api/3.19/sites/{self.site_luid}/workbooks/{workbook_id}/views/{view_name}/data"
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            # Parse the data response
            root = ET.fromstring(response.content)
            
            # Extract column information
            columns = []
            for column in root.findall('.//column'):
                col_info = {
                    'name': column.get('name'),
                    'data_type': column.get('dataType'),
                    'caption': column.get('caption')
                }
                columns.append(col_info)
            
            # Extract row data
            rows = []
            for row in root.findall('.//row'):
                row_data = []
                for cell in row.findall('.//cell'):
                    row_data.append(cell.text)
                rows.append(row_data)
            
            # Create DataFrame
            if columns and rows:
                column_names = [col['name'] for col in columns]
                df = pd.DataFrame(rows, columns=column_names)
                logger.info(f"Extracted {len(df)} rows from Tableau workbook {workbook_id}, view {view_name}")
                return df
            else:
                logger.warning(f"No data found in Tableau workbook {workbook_id}, view {view_name}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Failed to extract data from Tableau workbook {workbook_id}: {str(e)}")
            return pd.DataFrame()
    
    def get_student_analytics(self) -> pd.DataFrame:
        """Extract student analytics data from Tableau"""
        # This would typically connect to a specific workbook
        # For prototype, we'll return sample analytics data
        
        sample_data = [
            {
                'student_id': 'STU001',
                'course_id': 'CS101',
                'performance_score': 85.5,
                'engagement_level': 'High',
                'learning_style': 'Visual',
                'career_interest': 'Software Engineering',
                'skill_gaps': ['Machine Learning', 'System Design'],
                'recommended_courses': ['ML101', 'CS201'],
                'study_hours': 25,
                'assignment_completion_rate': 0.92,
                'quiz_average': 87.3,
                'participation_score': 8.5
            },
            {
                'student_id': 'STU002',
                'course_id': 'DS101',
                'performance_score': 92.0,
                'engagement_level': 'Very High',
                'learning_style': 'Kinesthetic',
                'career_interest': 'Data Science',
                'skill_gaps': ['Deep Learning', 'Statistics'],
                'recommended_courses': ['DL101', 'STAT201'],
                'study_hours': 30,
                'assignment_completion_rate': 0.96,
                'quiz_average': 91.8,
                'participation_score': 9.2
            },
            {
                'student_id': 'STU003',
                'course_id': 'BA101',
                'performance_score': 78.5,
                'engagement_level': 'Medium',
                'learning_style': 'Auditory',
                'career_interest': 'Product Management',
                'skill_gaps': ['User Research', 'Agile'],
                'recommended_courses': ['UX101', 'PM201'],
                'study_hours': 20,
                'assignment_completion_rate': 0.88,
                'quiz_average': 79.1,
                'participation_score': 7.8
            }
        ]
        
        df = pd.DataFrame(sample_data)
        logger.info(f"Extracted {len(df)} student analytics records from Tableau")
        return df
    
    def get_job_market_trends(self) -> pd.DataFrame:
        """Extract job market trends data from Tableau"""
        # Sample job market trends data
        sample_data = [
            {
                'skill': 'Python',
                'demand_score': 95,
                'salary_impact': 15,
                'growth_rate': 12.5,
                'job_postings_count': 1250,
                'average_salary': 95000,
                'trend_direction': 'Increasing'
            },
            {
                'skill': 'AWS',
                'demand_score': 88,
                'salary_impact': 18,
                'growth_rate': 15.2,
                'job_postings_count': 980,
                'average_salary': 105000,
                'trend_direction': 'Increasing'
            },
            {
                'skill': 'Machine Learning',
                'demand_score': 92,
                'salary_impact': 22,
                'growth_rate': 18.7,
                'job_postings_count': 750,
                'average_salary': 115000,
                'trend_direction': 'Increasing'
            },
            {
                'skill': 'Data Analysis',
                'demand_score': 85,
                'salary_impact': 12,
                'growth_rate': 8.3,
                'job_postings_count': 1100,
                'average_salary': 85000,
                'trend_direction': 'Stable'
            }
        ]
        
        df = pd.DataFrame(sample_data)
        logger.info(f"Extracted {len(df)} job market trend records from Tableau")
        return df
    
    def get_dashboard_metadata(self) -> Dict[str, Any]:
        """Get metadata about available dashboards and views"""
        try:
            workbooks = self.get_workbooks()
            
            metadata = {
                'total_workbooks': len(workbooks),
                'workbooks': workbooks,
                'last_updated': datetime.now().isoformat(),
                'available_views': [
                    'student_analytics',
                    'job_market_trends',
                    'course_performance',
                    'career_pathways'
                ]
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get dashboard metadata: {str(e)}")
            return {}
    
    def validate_data_quality(self, df: pd.DataFrame, data_source: str) -> Dict[str, Any]:
        """Validate data quality for Tableau extracted data"""
        validation_results = {
            'data_source': data_source,
            'total_records': len(df),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_records': df.duplicated().sum(),
            'validation_timestamp': datetime.now().isoformat()
        }
        
        # Check for required fields based on data source
        if data_source == 'student_analytics':
            required_fields = ['student_id', 'performance_score', 'engagement_level']
            for field in required_fields:
                if field in df.columns:
                    validation_results[f'{field}_completeness'] = (1 - df[field].isnull().sum() / len(df)) * 100
        
        return validation_results
    
    def close(self):
        """Sign out from Tableau Server"""
        if self.token:
            try:
                signout_url = f"{self.server_url}/api/3.19/auth/signout"
                self.session.post(signout_url)
                logger.info("Signed out from Tableau Server")
            except Exception as e:
                logger.warning(f"Failed to sign out from Tableau: {str(e)}")
        
        if self.session:
            self.session.close()
