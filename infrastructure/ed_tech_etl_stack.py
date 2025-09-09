"""
AWS CDK Stack for Ed-Tech ETL Pipeline
Creates S3 buckets, Glue jobs, Lambda functions, and CloudWatch monitoring
"""

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_glue as glue,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct


class EdTechETLStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Data Lake Bucket
        self.data_lake_bucket = s3.Bucket(
            self, "EdTechDataLake",
            bucket_name=f"ed-tech-data-lake-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="TransitionToIA",
                    enabled=True,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)
                        )
                    ]
                )
            ]
        )

        # IAM Role for Glue ETL Job
        self.glue_role = iam.Role(
            self, "GlueETLRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
            ],
            inline_policies={
                "S3Access": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:DeleteObject",
                                "s3:ListBucket"
                            ],
                            resources=[
                                self.data_lake_bucket.bucket_arn,
                                f"{self.data_lake_bucket.bucket_arn}/*"
                            ]
                        )
                    ]
                )
            }
        )

        # CloudWatch Log Group for ETL
        self.etl_log_group = logs.LogGroup(
            self, "ETLLogGroup",
            log_group_name="/aws/ed-tech/etl",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Glue ETL Job
        self.glue_job = glue.CfnJob(
            self, "EdTechETLJob",
            name="ed-tech-etl-job",
            role=self.glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=f"s3://{self.data_lake_bucket.bucket_name}/scripts/etl_script.py"
            ),
            max_capacity=2,
            timeout=60,
            glue_version="4.0",
            default_arguments={
                "--job-language": "python",
                "--job-bookmark-option": "job-bookmark-enable",
                "--enable-metrics": "true",
                "--enable-continuous-cloudwatch-log": "true",
                "--enable-continuous-log-filter": "true",
                "--continuous-log-logGroup": self.etl_log_group.log_group_name,
                "--continuous-log-logStreamPrefix": "glue-etl"
            }
        )

        # Lambda Function for Search
        self.search_lambda = lambda_.Function(
            self, "SearchFunction",
            function_name="ed-tech-search",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="search_handler.lambda_handler",
            code=lambda_.Code.from_asset("../lambda"),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "S3_BUCKET": self.data_lake_bucket.bucket_name,
                "SEARCH_INDEX_KEY": "search-index/student-resources.json"
            },
            log_retention=logs.RetentionDays.ONE_MONTH
        )

        # Grant Lambda access to S3
        self.data_lake_bucket.grant_read(self.search_lambda)

        # SNS Topic for Alerts
        self.alerts_topic = sns.Topic(
            self, "ETLAlertsTopic",
            display_name="Ed-Tech ETL Alerts"
        )

        # CloudWatch Alarms
        self.create_cloudwatch_alarms()

        # Outputs
        CfnOutput(
            self, "DataLakeBucketName",
            value=self.data_lake_bucket.bucket_name,
            description="S3 Data Lake Bucket Name"
        )
        
        CfnOutput(
            self, "SearchLambdaArn",
            value=self.search_lambda.function_arn,
            description="Search Lambda Function ARN"
        )

    def create_cloudwatch_alarms(self):
        """Create CloudWatch alarms for monitoring"""
        
        # ETL Job Failure Alarm
        etl_failure_alarm = cloudwatch.Alarm(
            self, "ETLJobFailureAlarm",
            alarm_name="ETLJobFailure",
            metric=cloudwatch.Metric(
                namespace="AWS/Glue",
                metric_name="glue.driver.aggregate.numFailedTasks",
                dimensions_map={
                    "JobName": self.glue_job.name
                }
            ),
            threshold=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            evaluation_periods=1,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
        )

        # Lambda Error Rate Alarm
        lambda_error_alarm = cloudwatch.Alarm(
            self, "LambdaErrorRateAlarm",
            alarm_name="LambdaErrorRate",
            metric=cloudwatch.Metric(
                namespace="AWS/Lambda",
                metric_name="Errors",
                dimensions_map={
                    "FunctionName": self.search_lambda.function_name
                }
            ),
            threshold=5,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            evaluation_periods=2,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
        )

        # Add SNS actions to alarms
        etl_failure_alarm.add_alarm_action(cw_actions.SnsAction(self.alerts_topic))
        lambda_error_alarm.add_alarm_action(cw_actions.SnsAction(self.alerts_topic))
