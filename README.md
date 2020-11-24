# covar-ingest

Coral reef covariates ingestion. This repo is for all the AWS deployment files and ingest code for various data sources.

## Deployment and Infrastructure

All AWS deployment will be managed using AWS CDK. All stacks for application deployments are located in the `deployment/` directory, and stacks for resources or services are in `infrastructure/`. Reference the deployment [README.md](deployment/README.md) for more details.

Link for installing AWS CDK: https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_install

## Lambda Functions

All lambda functions will be located under the `functions/` directory. Each sub directory is a lambda function. See the `functions/sample_ingest_function/` directory for a sample.

## Jobs

All Jobs will be located under the `jobs/` directory. Each jub directory is a job that will run in a container. See the `jobs/sample_ingest_job/` directory for a sample.

## Special Use Cases

There may be special use cases that these templates won't work for. Please reach out for help in those cases.
