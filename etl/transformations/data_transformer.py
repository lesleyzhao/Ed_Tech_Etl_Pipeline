"""
Data Transformation Module for Ed-Tech ETL Pipeline
Handles data cleaning, validation, and transformation logic
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class DataTransformer:
    """Data transformation and cleaning utilities"""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load data validation rules"""
        return {
            'student_id': {
                'pattern': r'^STU\d{3}$',
                'required': True,
                'type': str
            },
            'email': {
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'required': True,
                'type': str
            },
            'gpa': {
                'min': 0.0,
                'max': 4.0,
                'required': True,
                'type': float
            },
            'academic_program': {
                'required': True,
                'type': str,
                'allowed_values': [
                    'Computer Science', 'Data Science', 'Business Administration',
                    'Engineering', 'Mathematics', 'Statistics', 'Information Systems'
                ]
            }
        }
    
    def clean_text_data(self, text: str) -> str:
        """Clean and normalize text data"""
        if pd.isna(text) or text is None:
            return ""
        
        # Convert to string and strip whitespace
        cleaned = str(text).strip()
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove special characters except basic punctuation
        cleaned = re.sub(r'[^\w\s@.-]', '', cleaned)
        
        return cleaned
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if pd.isna(email) or email is None:
            return False
        
        pattern = self.validation_rules['email']['pattern']
        return bool(re.match(pattern, str(email)))
    
    def validate_student_id(self, student_id: str) -> bool:
        """Validate student ID format"""
        if pd.isna(student_id) or student_id is None:
            return False
        
        pattern = self.validation_rules['student_id']['pattern']
        return bool(re.match(pattern, str(student_id)))
    
    def clean_gpa(self, gpa: Any) -> Optional[float]:
        """Clean and validate GPA values"""
        if pd.isna(gpa) or gpa is None:
            return None
        
        try:
            gpa_float = float(gpa)
            if 0.0 <= gpa_float <= 4.0:
                return round(gpa_float, 2)
            else:
                logger.warning(f"GPA out of range: {gpa_float}")
                return None
        except (ValueError, TypeError):
            logger.warning(f"Invalid GPA format: {gpa}")
            return None
    
    def transform_oracle_data(self, oracle_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Transform Oracle data"""
        logger.info("Transforming Oracle data...")
        transformed_data = {}
        
        for table_name, df in oracle_data.items():
            if df.empty:
                logger.warning(f"Empty DataFrame for Oracle table: {table_name}")
                transformed_data[table_name] = df
                continue
            
            # Create a copy to avoid modifying original
            df_clean = df.copy()
            
            # Clean text columns
            text_columns = df_clean.select_dtypes(include=['object']).columns
            for col in text_columns:
                df_clean[col] = df_clean[col].apply(self.clean_text_data)
            
            # Specific transformations for each table
            if table_name == 'students':
                df_clean = self._transform_students_table(df_clean)
            elif table_name == 'courses':
                df_clean = self._transform_courses_table(df_clean)
            elif table_name == 'enrollments':
                df_clean = self._transform_enrollments_table(df_clean)
            elif table_name == 'academic_records':
                df_clean = self._transform_academic_records_table(df_clean)
            
            # Add data quality flags
            df_clean['data_quality_score'] = self._calculate_data_quality_score(df_clean, table_name)
            df_clean['transformed_at'] = datetime.now()
            
            transformed_data[table_name] = df_clean
            logger.info(f"Transformed Oracle {table_name}: {len(df_clean)} records")
        
        return transformed_data
    
    def _transform_students_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform students table"""
        # Clean and validate student IDs
        df['student_id'] = df['student_id'].apply(
            lambda x: x if self.validate_student_id(x) else None
        )
        
        # Clean and validate emails
        df['email'] = df['email'].apply(
            lambda x: x if self.validate_email(x) else None
        )
        
        # Clean GPA
        if 'gpa' in df.columns:
            df['gpa'] = df['gpa'].apply(self.clean_gpa)
        
        # Standardize academic program names
        if 'academic_program' in df.columns:
            df['academic_program'] = df['academic_program'].str.title()
        
        # Create full name
        if 'first_name' in df.columns and 'last_name' in df.columns:
            df['full_name'] = df['first_name'] + ' ' + df['last_name']
        
        return df
    
    def _transform_courses_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform courses table"""
        # Clean course codes
        if 'course_code' in df.columns:
            df['course_code'] = df['course_code'].str.upper().str.strip()
        
        # Clean course names
        if 'course_name' in df.columns:
            df['course_name'] = df['course_name'].str.title()
        
        # Clean credits
        if 'credits' in df.columns:
            df['credits'] = pd.to_numeric(df['credits'], errors='coerce')
        
        return df
    
    def _transform_enrollments_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform enrollments table"""
        # Clean grades
        if 'grade' in df.columns:
            df['grade'] = df['grade'].str.upper().str.strip()
        
        # Convert dates
        date_columns = ['enrollment_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def _transform_academic_records_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform academic records table"""
        # Clean GPA
        if 'gpa' in df.columns:
            df['gpa'] = df['gpa'].apply(self.clean_gpa)
        
        # Clean credits
        if 'total_credits' in df.columns:
            df['total_credits'] = pd.to_numeric(df['total_credits'], errors='coerce')
        
        # Convert dates
        date_columns = ['year']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def transform_workday_data(self, workday_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Transform Workday data"""
        logger.info("Transforming Workday data...")
        transformed_data = {}
        
        for dataset_name, df in workday_data.items():
            if df.empty:
                logger.warning(f"Empty DataFrame for Workday dataset: {dataset_name}")
                transformed_data[dataset_name] = df
                continue
            
            df_clean = df.copy()
            
            # Clean text columns
            text_columns = df_clean.select_dtypes(include=['object']).columns
            for col in text_columns:
                df_clean[col] = df_clean[col].apply(self.clean_text_data)
            
            # Specific transformations
            if dataset_name == 'students':
                df_clean = self._transform_workday_students(df_clean)
            elif dataset_name == 'job_postings':
                df_clean = self._transform_workday_jobs(df_clean)
            
            # Add metadata
            df_clean['data_source'] = 'workday'
            df_clean['transformed_at'] = datetime.now()
            
            transformed_data[dataset_name] = df_clean
            logger.info(f"Transformed Workday {dataset_name}: {len(df_clean)} records")
        
        return transformed_data
    
    def _transform_workday_students(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform Workday students data"""
        # Clean student IDs
        if 'student_id' in df.columns:
            df['student_id'] = df['student_id'].str.upper().str.strip()
        
        # Clean emails
        if 'email' in df.columns:
            df['email'] = df['email'].apply(
                lambda x: x if self.validate_email(x) else None
            )
        
        # Clean GPA
        if 'gpa' in df.columns:
            df['gpa'] = df['gpa'].apply(self.clean_gpa)
        
        return df
    
    def _transform_workday_jobs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform Workday job postings data"""
        # Clean job titles
        if 'job_title' in df.columns:
            df['job_title'] = df['job_title'].str.title()
        
        # Clean company names
        if 'company' in df.columns:
            df['company'] = df['company'].str.title()
        
        # Clean locations
        if 'location' in df.columns:
            df['location'] = df['location'].str.title()
        
        # Process salary ranges
        if 'salary_range' in df.columns:
            df['salary_range'] = df['salary_range'].apply(self._clean_salary_range)
        
        # Process skills lists
        skill_columns = ['required_skills', 'preferred_skills']
        for col in skill_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._clean_skills_list)
        
        return df
    
    def _clean_salary_range(self, salary: str) -> str:
        """Clean salary range data"""
        if pd.isna(salary) or salary is None:
            return ""
        
        # Remove currency symbols and normalize
        cleaned = str(salary).replace('$', '').replace(',', '').strip()
        
        # Extract numeric ranges
        numbers = re.findall(r'\d+', cleaned)
        if len(numbers) >= 2:
            return f"{numbers[0]}-{numbers[1]}"
        elif len(numbers) == 1:
            return numbers[0]
        else:
            return cleaned
    
    def _clean_skills_list(self, skills: Any) -> List[str]:
        """Clean and normalize skills list"""
        if pd.isna(skills) or skills is None:
            return []
        
        if isinstance(skills, list):
            return [self.clean_text_data(skill) for skill in skills if skill]
        elif isinstance(skills, str):
            # Split by common delimiters
            skills_list = re.split(r'[,;|]', skills)
            return [self.clean_text_data(skill) for skill in skills_list if skill.strip()]
        else:
            return []
    
    def transform_tableau_data(self, tableau_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Transform Tableau data"""
        logger.info("Transforming Tableau data...")
        transformed_data = {}
        
        for dataset_name, df in tableau_data.items():
            if df.empty:
                logger.warning(f"Empty DataFrame for Tableau dataset: {dataset_name}")
                transformed_data[dataset_name] = df
                continue
            
            df_clean = df.copy()
            
            # Clean text columns
            text_columns = df_clean.select_dtypes(include=['object']).columns
            for col in text_columns:
                df_clean[col] = df_clean[col].apply(self.clean_text_data)
            
            # Clean numeric columns
            numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
            # Add metadata
            df_clean['data_source'] = 'tableau'
            df_clean['transformed_at'] = datetime.now()
            
            transformed_data[dataset_name] = df_clean
            logger.info(f"Transformed Tableau {dataset_name}: {len(df_clean)} records")
        
        return transformed_data
    
    def create_unified_datasets(self, transformed_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Create unified datasets from all transformed data"""
        logger.info("Creating unified datasets...")
        unified_data = {}
        
        try:
            # Create unified student profiles
            student_profiles = self._create_unified_student_profiles(transformed_data)
            unified_data['student_profiles'] = student_profiles
            
            # Create job recommendations
            job_recommendations = self._create_job_recommendations(transformed_data)
            unified_data['job_recommendations'] = job_recommendations
            
            # Create course recommendations
            course_recommendations = self._create_course_recommendations(transformed_data)
            unified_data['course_recommendations'] = course_recommendations
            
            logger.info(f"Created {len(unified_data)} unified datasets")
            return unified_data
            
        except Exception as e:
            logger.error(f"Failed to create unified datasets: {str(e)}")
            return {}
    
    def _create_unified_student_profiles(self, transformed_data: Dict[str, Any]) -> pd.DataFrame:
        """Create unified student profiles from all sources"""
        student_profiles = []
        
        # Get students from Oracle
        if 'oracle' in transformed_data and 'students' in transformed_data['oracle']:
            oracle_students = transformed_data['oracle']['students']
            for _, row in oracle_students.iterrows():
                profile = {
                    'student_id': row.get('student_id'),
                    'first_name': row.get('first_name'),
                    'last_name': row.get('last_name'),
                    'email': row.get('email'),
                    'academic_program': row.get('academic_program'),
                    'gpa': row.get('gpa'),
                    'enrollment_date': row.get('enrollment_date'),
                    'graduation_date': row.get('graduation_date'),
                    'status': row.get('status'),
                    'data_source': 'oracle'
                }
                student_profiles.append(profile)
        
        # Get students from Workday
        if 'workday' in transformed_data and 'students' in transformed_data['workday']:
            workday_students = transformed_data['workday']['students']
            for _, row in workday_students.iterrows():
                profile = {
                    'student_id': row.get('student_id'),
                    'first_name': row.get('first_name'),
                    'last_name': row.get('last_name'),
                    'email': row.get('email'),
                    'academic_program': row.get('academic_program'),
                    'gpa': row.get('gpa'),
                    'enrollment_date': row.get('enrollment_date'),
                    'graduation_date': row.get('expected_graduation'),
                    'status': row.get('status'),
                    'data_source': 'workday'
                }
                student_profiles.append(profile)
        
        # Add analytics data from Tableau
        if 'tableau' in transformed_data and 'student_analytics' in transformed_data['tableau']:
            analytics = transformed_data['tableau']['student_analytics']
            for _, row in analytics.iterrows():
                # Find matching student profile
                student_id = row.get('student_id')
                for profile in student_profiles:
                    if profile['student_id'] == student_id:
                        profile.update({
                            'performance_score': row.get('performance_score'),
                            'engagement_level': row.get('engagement_level'),
                            'learning_style': row.get('learning_style'),
                            'career_interest': row.get('career_interest'),
                            'skill_gaps': row.get('skill_gaps', []),
                            'recommended_courses': row.get('recommended_courses', [])
                        })
                        break
        
        return pd.DataFrame(student_profiles)
    
    def _create_job_recommendations(self, transformed_data: Dict[str, Any]) -> pd.DataFrame:
        """Create job recommendations based on student profiles and job postings"""
        job_recommendations = []
        
        # Get job postings from Workday
        if 'workday' in transformed_data and 'job_postings' in transformed_data['workday']:
            job_postings = transformed_data['workday']['job_postings']
            
            # Get student profiles for matching
            student_profiles = []
            if 'oracle' in transformed_data and 'students' in transformed_data['oracle']:
                student_profiles.extend(transformed_data['oracle']['students'].to_dict('records'))
            if 'workday' in transformed_data and 'students' in transformed_data['workday']:
                student_profiles.extend(transformed_data['workday']['students'].to_dict('records'))
            
            # Create job recommendations (simplified matching logic)
            for _, job in job_postings.iterrows():
                for student in student_profiles:
                    # Simple matching based on academic program and skills
                    match_score = self._calculate_job_match_score(student, job)
                    
                    if match_score > 0.5:  # Threshold for recommendations
                        recommendation = {
                            'student_id': student.get('student_id'),
                            'job_posting_id': job.get('job_posting_id'),
                            'job_title': job.get('job_title'),
                            'company': job.get('company'),
                            'location': job.get('location'),
                            'required_skills': job.get('required_skills', []),
                            'salary_range': job.get('salary_range'),
                            'match_score': match_score,
                            'match_reasons': self._get_match_reasons(student, job),
                            'created_at': datetime.now()
                        }
                        job_recommendations.append(recommendation)
        
        return pd.DataFrame(job_recommendations)
    
    def _create_course_recommendations(self, transformed_data: Dict[str, Any]) -> pd.DataFrame:
        """Create course recommendations based on skill gaps and career interests"""
        course_recommendations = []
        
        # Get student analytics from Tableau
        if 'tableau' in transformed_data and 'student_analytics' in transformed_data['tableau']:
            analytics = transformed_data['tableau']['student_analytics']
            
            for _, row in analytics.iterrows():
                student_id = row.get('student_id')
                skill_gaps = row.get('skill_gaps', [])
                recommended_courses = row.get('recommended_courses', [])
                career_interest = row.get('career_interest')
                
                for course in recommended_courses:
                    recommendation = {
                        'student_id': student_id,
                        'course_id': course,
                        'course_name': f"Course {course}",
                        'reason': f"Addresses skill gap: {', '.join(skill_gaps[:2])}",
                        'career_relevance': career_interest,
                        'priority': 'High' if course in skill_gaps else 'Medium',
                        'created_at': datetime.now()
                    }
                    course_recommendations.append(recommendation)
        
        return pd.DataFrame(course_recommendations)
    
    def _calculate_job_match_score(self, student: Dict[str, Any], job: Dict[str, Any]) -> float:
        """Calculate job match score between student and job"""
        score = 0.0
        
        # Academic program match
        student_program = student.get('academic_program', '').lower()
        job_skills = [skill.lower() for skill in job.get('required_skills', [])]
        
        if 'computer science' in student_program and any('programming' in skill for skill in job_skills):
            score += 0.3
        elif 'data science' in student_program and any('data' in skill for skill in job_skills):
            score += 0.3
        elif 'business' in student_program and any('management' in skill for skill in job_skills):
            score += 0.3
        
        # GPA consideration
        student_gpa = student.get('gpa', 0)
        if student_gpa and student_gpa >= 3.5:
            score += 0.2
        
        # Skills overlap
        student_skills = student.get('skill_gaps', [])
        skill_overlap = len(set(student_skills) & set(job_skills))
        if skill_overlap > 0:
            score += min(0.5, skill_overlap * 0.1)
        
        return min(1.0, score)
    
    def _get_match_reasons(self, student: Dict[str, Any], job: Dict[str, Any]) -> List[str]:
        """Get reasons for job match"""
        reasons = []
        
        student_program = student.get('academic_program', '').lower()
        if 'computer science' in student_program:
            reasons.append("Computer Science background")
        elif 'data science' in student_program:
            reasons.append("Data Science background")
        
        student_gpa = student.get('gpa', 0)
        if student_gpa and student_gpa >= 3.5:
            reasons.append("Strong academic performance")
        
        return reasons
    
    def _calculate_data_quality_score(self, df: pd.DataFrame, table_name: str) -> float:
        """Calculate data quality score for a dataset"""
        if df.empty:
            return 0.0
        
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        
        # Base score from completeness
        completeness_score = (total_cells - null_cells) / total_cells
        
        # Additional quality checks
        quality_penalty = 0.0
        
        # Check for duplicates
        duplicate_ratio = df.duplicated().sum() / len(df)
        quality_penalty += duplicate_ratio * 0.1
        
        # Check for data type consistency
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for inconsistent formats
                unique_values = df[col].dropna().nunique()
                if unique_values > 0:
                    consistency_ratio = unique_values / len(df[col].dropna())
                    if consistency_ratio > 0.8:  # Too many unique values might indicate inconsistency
                        quality_penalty += 0.05
        
        final_score = max(0.0, completeness_score - quality_penalty)
        return round(final_score, 3)
