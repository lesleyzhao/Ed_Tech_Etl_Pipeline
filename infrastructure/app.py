#!/usr/bin/env python3
"""
AWS CDK App for Ed-Tech ETL Pipeline Infrastructure
"""

import aws_cdk as cdk
from ed_tech_etl_stack import EdTechETLStack

app = cdk.App()

# Create the main ETL stack
EdTechETLStack(
    app, 
    "EdTechETLPipeline",
    description="Ed-Tech ETL Pipeline with Glue, Lambda, and S3",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    )
)

app.synth()
