#!/usr/bin/env python3

from aws_cdk import core

from infrastructure.vpc import BaseInfrastructure
from deployment.sample_lambda_stack import SampleLambdaIngestStack
from deployment.dhw_ingest import DhwIngestStack
from deployment.npp_ingest import NPPIngestStack

DEPLOY_ENV = core.Environment(account='138863487738', region='us-east-1')

app = core.App()

##  Development Stacks  ##

# Infrastructure
infra = BaseInfrastructure(
    app, 'dev-base-infrastructure', cidr_block='10.0.0.0/16', env=DEPLOY_ENV
)

# Applications

# SampleLambdaIngestStack(app, "sample-lambda-ingest-dev", env=DEPLOY_ENV)

DhwIngestStack(
    app,
    'dhw-ingest-job-dev',
    env=DEPLOY_ENV
)

NPPIngestStack(
    app,
    'npp-ingest-job-dev',
    env=DEPLOY_ENV
)

## Production Stacks ##

app.synth()
