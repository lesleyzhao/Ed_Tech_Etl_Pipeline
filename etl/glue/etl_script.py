"""
AWS Glue ETL Script for Ed-Tech Data Pipeline
Processes data from Oracle, Workday, and Tableau sources
"""

import sys
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *
import json
from datetime import datetime

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# S3 client for metadata operations
s3_client = boto3.client('s3')

def extract_oracle_data():
    """Extract data from Oracle database"""
    print("Extracting data from Oracle...")
    
    # Oracle connection parameters (in production, use AWS Secrets Manager)
    oracle_connection_options = {
        "url": "jdbc:oracle:thin://oracle-db.example.com:1521/EDTECH",
        "dbtable": "students",
        "user": "etl_user",
        "password": "etl_password"
    }
    
    # Extract students data
    students_df = glueContext.create_dynamic_frame.from_options(
        connection_type="oracle",
        connection_options=oracle_connection_options
    ).toDF()
    
    # Extract courses data
    courses_connection_options = oracle_connection_options.copy()
    courses_connection_options["dbtable"] = "courses"
    courses_df = glueContext.create_dynamic_frame.from_options(
        connection_type="oracle",
        connection_options=courses_connection_options
    ).toDF()
    
    # Extract enrollments data
    enrollments_connection_options = oracle_connection_options.copy()
    enrollments_connection_options["dbtable"] = "enrollments"
    enrollments_df = glueContext.create_dynamic_frame.from_options(
        connection_type="oracle",
        connection_options=enrollments_connection_options
    ).toDF()
    
    return students_df, courses_df, enrollments_df

def extract_workday_data():
    """Extract data from Workday API"""
    print("Extracting data from Workday...")
    
    # In production, this would make actual API calls to Workday
    # For prototype, we'll create sample data
    workday_schema = StructType([
        StructField("student_id", StringType(), True),
        StructField("academic_program", StringType(), True),
        StructField("graduation_date", DateType(), True),
        StructField("gpa", DoubleType(), True),
        StructField("job_posting_id", StringType(), True),
        StructField("job_title", StringType(), True),
        StructField("company", StringType(), True),
        StructField("location", StringType(), True),
        StructField("required_skills", ArrayType(StringType()), True),
        StructField("salary_range", StringType(), True),
        StructField("posting_date", TimestampType(), True)
    ])
    
    # Sample Workday data
    sample_data = [
        ("STU001", "Computer Science", "2024-05-15", 3.8, "JOB001", 
         "Software Engineer", "Tech Corp", "San Francisco, CA", 
         ["Python", "AWS", "Docker"], "80k-120k", "2024-01-15 10:00:00"),
        ("STU002", "Data Science", "2024-05-15", 3.6, "JOB002", 
         "Data Analyst", "Data Inc", "New York, NY", 
         ["SQL", "Python", "Tableau"], "70k-100k", "2024-01-16 14:30:00"),
        ("STU003", "Business Administration", "2024-05-15", 3.9, "JOB003", 
         "Product Manager", "StartupXYZ", "Austin, TX", 
         ["Agile", "Product Management", "Analytics"], "90k-130k", "2024-01-17 09:15:00")
    ]
    
    workday_df = spark.createDataFrame(sample_data, workday_schema)
    return workday_df

def extract_tableau_data():
    """Extract data from Tableau workbooks"""
    print("Extracting data from Tableau...")
    
    # In production, this would connect to Tableau Server API
    # For prototype, we'll create sample analytics data
    tableau_schema = StructType([
        StructField("student_id", StringType(), True),
        StructField("course_id", StringType(), True),
        StructField("performance_score", DoubleType(), True),
        StructField("engagement_level", StringType(), True),
        StructField("learning_style", StringType(), True),
        StructField("career_interest", StringType(), True),
        StructField("skill_gaps", ArrayType(StringType()), True),
        StructField("recommended_courses", ArrayType(StringType()), True)
    ])
    
    # Sample Tableau analytics data
    sample_data = [
        ("STU001", "CS101", 85.5, "High", "Visual", "Software Engineering", 
         ["Machine Learning", "System Design"], ["ML101", "CS201"]),
        ("STU002", "DS101", 92.0, "Very High", "Kinesthetic", "Data Science", 
         ["Deep Learning", "Statistics"], ["DL101", "STAT201"]),
        ("STU003", "BA101", 78.5, "Medium", "Auditory", "Product Management", 
         ["User Research", "Agile"], ["UX101", "PM201"])
    ]
    
    tableau_df = spark.createDataFrame(sample_data, tableau_schema)
    return tableau_df

def transform_and_join_data(students_df, courses_df, enrollments_df, workday_df, tableau_df):
    """Transform and join all data sources"""
    print("Transforming and joining data...")
    
    # Add data source identifiers
    students_df = students_df.withColumn("data_source", F.lit("oracle"))
    courses_df = courses_df.withColumn("data_source", F.lit("oracle"))
    enrollments_df = enrollments_df.withColumn("data_source", F.lit("oracle"))
    workday_df = workday_df.withColumn("data_source", F.lit("workday"))
    tableau_df = tableau_df.withColumn("data_source", F.lit("tableau"))
    
    # Add processing timestamp
    current_timestamp = datetime.now()
    students_df = students_df.withColumn("processed_at", F.lit(current_timestamp))
    courses_df = courses_df.withColumn("processed_at", F.lit(current_timestamp))
    enrollments_df = enrollments_df.withColumn("processed_at", F.lit(current_timestamp))
    workday_df = workday_df.withColumn("processed_at", F.lit(current_timestamp))
    tableau_df = tableau_df.withColumn("processed_at", F.lit(current_timestamp))
    
    # Create unified student profile
    student_profiles = students_df.join(
        tableau_df.select("student_id", "performance_score", "engagement_level", 
                         "learning_style", "career_interest", "skill_gaps", 
                         "recommended_courses"),
        "student_id", "left"
    )
    
    # Create job recommendations based on student profiles and job postings
    job_recommendations = workday_df.select(
        "student_id", "job_posting_id", "job_title", "company", "location",
        "required_skills", "salary_range", "posting_date"
    ).withColumn("match_score", F.lit(0.85))  # In production, calculate based on ML model
    
    return student_profiles, job_recommendations

def create_search_index(student_profiles, job_recommendations):
    """Create search index for Lambda function"""
    print("Creating search index...")
    
    # Combine student profiles with job recommendations
    search_data = student_profiles.join(
        job_recommendations,
        "student_id",
        "left"
    ).select(
        "student_id",
        "academic_program",
        "gpa",
        "performance_score",
        "engagement_level",
        "learning_style",
        "career_interest",
        "skill_gaps",
        "recommended_courses",
        "job_title",
        "company",
        "location",
        "required_skills",
        "salary_range",
        "match_score",
        "processed_at"
    )
    
    # Convert to JSON for search index
    search_index = search_data.toJSON().collect()
    
    return search_index

def load_to_s3(dataframes, search_index, bucket_name):
    """Load processed data to S3"""
    print("Loading data to S3...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Load raw data
    for name, df in dataframes.items():
        df.write.mode("overwrite").parquet(
            f"s3://{bucket_name}/processed/{name}/{timestamp}/"
        )
    
    # Load search index
    search_index_json = {
        "index_created_at": datetime.now().isoformat(),
        "total_records": len(search_index),
        "records": [json.loads(record) for record in search_index]
    }
    
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"search-index/student-resources.json",
        Body=json.dumps(search_index_json, indent=2),
        ContentType="application/json"
    )
    
    print(f"Search index created with {len(search_index)} records")

def main():
    """Main ETL pipeline execution"""
    try:
        print("Starting Ed-Tech ETL Pipeline...")
        
        # Get S3 bucket name from environment or use default
        bucket_name = "ed-tech-data-lake-123456789012"  # Replace with actual bucket
        
        # Extract data from all sources
        students_df, courses_df, enrollments_df = extract_oracle_data()
        workday_df = extract_workday_data()
        tableau_df = extract_tableau_data()
        
        # Transform and join data
        student_profiles, job_recommendations = transform_and_join_data(
            students_df, courses_df, enrollments_df, workday_df, tableau_df
        )
        
        # Create search index
        search_index = create_search_index(student_profiles, job_recommendations)
        
        # Load to S3
        dataframes = {
            "students": students_df,
            "courses": courses_df,
            "enrollments": enrollments_df,
            "workday_jobs": workday_df,
            "tableau_analytics": tableau_df,
            "student_profiles": student_profiles,
            "job_recommendations": job_recommendations
        }
        
        load_to_s3(dataframes, search_index, bucket_name)
        
        print("ETL Pipeline completed successfully!")
        
        # Log metrics for monitoring
        print(f"Processed {student_profiles.count()} student profiles")
        print(f"Processed {job_recommendations.count()} job recommendations")
        print(f"Created search index with {len(search_index)} records")
        
    except Exception as e:
        print(f"ETL Pipeline failed: {str(e)}")
        raise e
    finally:
        job.commit()

if __name__ == "__main__":
    main()
