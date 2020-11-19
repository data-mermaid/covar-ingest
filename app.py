#!/usr/bin/env python3

from aws_cdk import core

from infrastructure.vpc import BaseInfrastructure
from deployment.sample_lambda_stack import SampleLambdaIngestStack
from deployment.sample_job_stack import SampleJobIngestStack
from deployment.npp_ingest import NPPIngestStack

DEPLOY_ENV = core.Environment(account='138863487738', region='us-east-1')

app = core.App()

# Infrastructure
infra = BaseInfrastructure(
    app, 'base-infrastructure', cidr_block='10.0.0.0/16', env=DEPLOY_ENV
)

# Applications
# SampleLambdaIngestStack(app, "sample-lambda-ingest-dev", env=DEPLOY_ENV)
# SampleJobIngestStack(app, 'sample-job-ingest-dev', env=DEPLOY_ENV)

NPPIngestStack(
    app, 
    'npp-ingest-job-dev', 
    env=DEPLOY_ENV
)

app.synth()
