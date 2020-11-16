#!/usr/bin/env python3

from aws_cdk import core

from deployment.sample_lambda_stack import SampleIngestStack

DEPLOY_ENV = core.Environment(
    account='',
    region=''
)

app = core.App()

SampleIngestStack(app, "sample-ingest-dev")

app.synth()
