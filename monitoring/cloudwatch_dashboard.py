"""
CloudWatch Dashboard Configuration for Ed-Tech ETL Pipeline
Creates comprehensive monitoring dashboards and alarms
"""

import boto3
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

class CloudWatchMonitoring:
    """CloudWatch monitoring setup for ETL pipeline"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
    
    def create_etl_dashboard(self) -> str:
        """Create comprehensive ETL monitoring dashboard"""
        
        dashboard_body = {
            "widgets": [
                {
                    "type": "metric",
                    "x": 0,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/Glue", "glue.driver.aggregate.numCompletedTasks", "JobName", "ed-tech-etl-job"],
                            ["AWS/Glue", "glue.driver.aggregate.numFailedTasks", "JobName", "ed-tech-etl-job"],
                            ["AWS/Glue", "glue.driver.aggregate.numRunningTasks", "JobName", "ed-tech-etl-job"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "ETL Job Task Status",
                        "period": 300,
                        "stat": "Sum"
                    }
                },
                {
                    "type": "metric",
                    "x": 12,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/Glue", "glue.driver.aggregate.bytesRead", "JobName", "ed-tech-etl-job"],
                            ["AWS/Glue", "glue.driver.aggregate.bytesWritten", "JobName", "ed-tech-etl-job"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "ETL Data Processing Volume",
                        "period": 300,
                        "stat": "Sum",
                        "yAxis": {
                            "left": {
                                "min": 0
                            }
                        }
                    }
                },
                {
                    "type": "metric",
                    "x": 0,
                    "y": 6,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/Lambda", "Invocations", "FunctionName", "ed-tech-search"],
                            ["AWS/Lambda", "Errors", "FunctionName", "ed-tech-search"],
                            ["AWS/Lambda", "Duration", "FunctionName", "ed-tech-search"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "Lambda Search Function Performance",
                        "period": 300,
                        "stat": "Sum"
                    }
                },
                {
                    "type": "metric",
                    "x": 12,
                    "y": 6,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/S3", "BucketSizeBytes", "BucketName", "ed-tech-data-lake-123456789012", "StorageType", "StandardStorage"],
                            ["AWS/S3", "NumberOfObjects", "BucketName", "ed-tech-data-lake-123456789012", "StorageType", "AllStorageTypes"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "S3 Data Lake Storage",
                        "period": 86400,
                        "stat": "Average"
                    }
                },
                {
                    "type": "metric",
                    "x": 0,
                    "y": 12,
                    "width": 24,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["EdTech/ETL", "RecordsProcessed"],
                            ["EdTech/ETL", "ProcessingTime"],
                            ["EdTech/Search", "SearchRequests"],
                            ["EdTech/Search", "SearchResults"],
                            ["EdTech/Search", "SearchErrors"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "Custom ETL and Search Metrics",
                        "period": 300,
                        "stat": "Sum"
                    }
                }
            ]
        }
        
        try:
            response = self.cloudwatch.put_dashboard(
                DashboardName='EdTech-ETL-Pipeline',
                DashboardBody=json.dumps(dashboard_body)
            )
            print("ETL Dashboard created successfully")
            return response['DashboardUrl']
        except Exception as e:
            print(f"Failed to create ETL dashboard: {str(e)}")
            return None
    
    def create_search_dashboard(self) -> str:
        """Create search function monitoring dashboard"""
        
        dashboard_body = {
            "widgets": [
                {
                    "type": "metric",
                    "x": 0,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/Lambda", "Invocations", "FunctionName", "ed-tech-search"],
                            ["AWS/Lambda", "Errors", "FunctionName", "ed-tech-search"],
                            ["AWS/Lambda", "Throttles", "FunctionName", "ed-tech-search"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "Search Function Invocations",
                        "period": 300,
                        "stat": "Sum"
                    }
                },
                {
                    "type": "metric",
                    "x": 12,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/Lambda", "Duration", "FunctionName", "ed-tech-search"],
                            ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", "ed-tech-search"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "Search Function Performance",
                        "period": 300,
                        "stat": "Average"
                    }
                },
                {
                    "type": "metric",
                    "x": 0,
                    "y": 6,
                    "width": 24,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["EdTech/Search", "SearchRequests"],
                            ["EdTech/Search", "SearchResults"],
                            ["EdTech/Search", "SearchErrors"],
                            ["EdTech/Search", "AverageResponseTime"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.region,
                        "title": "Search Performance Metrics",
                        "period": 300,
                        "stat": "Sum"
                    }
                }
            ]
        }
        
        try:
            response = self.cloudwatch.put_dashboard(
                DashboardName='EdTech-Search-Function',
                DashboardBody=json.dumps(dashboard_body)
            )
            print("Search Dashboard created successfully")
            return response['DashboardUrl']
        except Exception as e:
            print(f"Failed to create search dashboard: {str(e)}")
            return None
    
    def create_alarms(self) -> List[str]:
        """Create CloudWatch alarms for monitoring"""
        alarms_created = []
        
        # ETL Job Failure Alarm
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName='ETLJobFailure',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='glue.driver.aggregate.numFailedTasks',
                Namespace='AWS/Glue',
                Period=300,
                Statistic='Sum',
                Threshold=1.0,
                ActionsEnabled=True,
                AlarmDescription='Alert when ETL job has failed tasks',
                Dimensions=[
                    {
                        'Name': 'JobName',
                        'Value': 'ed-tech-etl-job'
                    }
                ]
            )
            alarms_created.append('ETLJobFailure')
        except Exception as e:
            print(f"Failed to create ETL failure alarm: {str(e)}")
        
        # Lambda Error Rate Alarm
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName='LambdaErrorRate',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=2,
                MetricName='Errors',
                Namespace='AWS/Lambda',
                Period=300,
                Statistic='Sum',
                Threshold=5.0,
                ActionsEnabled=True,
                AlarmDescription='Alert when Lambda error rate is high',
                Dimensions=[
                    {
                        'Name': 'FunctionName',
                        'Value': 'ed-tech-search'
                    }
                ]
            )
            alarms_created.append('LambdaErrorRate')
        except Exception as e:
            print(f"Failed to create Lambda error alarm: {str(e)}")
        
        # S3 Storage Alarm
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName='S3StorageHigh',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='BucketSizeBytes',
                Namespace='AWS/S3',
                Period=86400,
                Statistic='Average',
                Threshold=1000000000000,  # 1TB
                ActionsEnabled=True,
                AlarmDescription='Alert when S3 storage exceeds 1TB',
                Dimensions=[
                    {
                        'Name': 'BucketName',
                        'Value': 'ed-tech-data-lake-123456789012'
                    },
                    {
                        'Name': 'StorageType',
                        'Value': 'StandardStorage'
                    }
                ]
            )
            alarms_created.append('S3StorageHigh')
        except Exception as e:
            print(f"Failed to create S3 storage alarm: {str(e)}")
        
        return alarms_created
    
    def create_log_groups(self) -> List[str]:
        """Create CloudWatch log groups"""
        log_groups_created = []
        
        log_groups = [
            '/aws/ed-tech/etl',
            '/aws/lambda/ed-tech-search',
            '/aws/glue/ed-tech-etl-job'
        ]
        
        for log_group in log_groups:
            try:
                self.logs.create_log_group(
                    logGroupName=log_group,
                    retentionInDays=30
                )
                log_groups_created.append(log_group)
            except self.logs.exceptions.ResourceAlreadyExistsException:
                print(f"Log group {log_group} already exists")
            except Exception as e:
                print(f"Failed to create log group {log_group}: {str(e)}")
        
        return log_groups_created
    
    def send_custom_metrics(self, metrics: Dict[str, float]):
        """Send custom metrics to CloudWatch"""
        try:
            metric_data = []
            for metric_name, value in metrics.items():
                metric_data.append({
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow()
                })
            
            self.cloudwatch.put_metric_data(
                Namespace='EdTech/ETL',
                MetricData=metric_data
            )
            print(f"Sent {len(metric_data)} custom metrics to CloudWatch")
        except Exception as e:
            print(f"Failed to send custom metrics: {str(e)}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of key metrics"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            # Get ETL job metrics
            etl_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/Glue',
                MetricName='glue.driver.aggregate.numCompletedTasks',
                Dimensions=[
                    {
                        'Name': 'JobName',
                        'Value': 'ed-tech-etl-job'
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            
            # Get Lambda metrics
            lambda_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Invocations',
                Dimensions=[
                    {
                        'Name': 'FunctionName',
                        'Value': 'ed-tech-search'
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            
            return {
                'etl_completed_tasks': sum([point['Sum'] for point in etl_metrics['Datapoints']]),
                'lambda_invocations': sum([point['Sum'] for point in lambda_metrics['Datapoints']]),
                'time_range': f"{start_time} to {end_time}",
                'last_updated': datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Failed to get metrics summary: {str(e)}")
            return {}

def main():
    """Main function to set up monitoring"""
    monitoring = CloudWatchMonitoring()
    
    print("Setting up CloudWatch monitoring...")
    
    # Create dashboards
    etl_dashboard_url = monitoring.create_etl_dashboard()
    search_dashboard_url = monitoring.create_search_dashboard()
    
    # Create alarms
    alarms = monitoring.create_alarms()
    
    # Create log groups
    log_groups = monitoring.create_log_groups()
    
    print(f"ETL Dashboard: {etl_dashboard_url}")
    print(f"Search Dashboard: {search_dashboard_url}")
    print(f"Created alarms: {alarms}")
    print(f"Created log groups: {log_groups}")

if __name__ == "__main__":
    main()
