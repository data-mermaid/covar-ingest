from aws_cdk import (
    core,
    aws_batch as batch,
    aws_ecs as ecs,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam
)


class SampleJobIngestStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, job_role: iam.Role, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        job_name = 'npp-batch-job'
        
        batch.JobDefinition(
            self,
            job_name,
            # Use a readable name for executing.
            job_definition_name=job_name,
            container=batch.JobDefinitionContainer(
                # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_batch/JobDefinitionContainer.html
                image=ecs.ContainerImage.from_asset(
                    "./jobs/car-detection/",
                ),
                job_role=job_role,
                memory_limit_mib=16384,
                vcpus=1,
                environment={
                    "ENV": "",
                    "AWS_BUCKET": "covariate-ingest-data",
                    "STAC_API": ""
                },
                privileged=False,
            ),
            # retry_attempts=3,
            # parameters={'param1': "value1"},
            # timeout=, # Object aws_cdk.core.Duration
        )