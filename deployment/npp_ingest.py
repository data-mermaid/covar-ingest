from aws_cdk import (
    core,
    aws_batch as batch,
    aws_ecs as ecs,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam
)


class NPPIngestStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        job_name = 'npp-batch-job'

        # TODO pass this in somehow, SSM?
        job_role = iam.Role.from_role_arn(
            self, 'job-role',
            role_arn='arn:aws:iam::138863487738:role/covariate-ingest-batch-job'
        )

        # TODO pass this in somehow, SSM?
        job_queue = batch.JobQueue.from_job_queue_arn(
            self, 'batch-queue',
            job_queue_arn='arn:aws:batch:us-east-1:138863487738:job-queue/covariate-ingest-cpu-queue'
        )
        
        npp_job = batch.JobDefinition(
            self,
            job_name,
            # Use a readable name for executing.
            job_definition_name=job_name,
            container=batch.JobDefinitionContainer(
                # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_batch/JobDefinitionContainer.html
                image=ecs.ContainerImage.from_asset(
                    "./jobs/npp/",
                ),
                job_role=job_role,
                memory_limit_mib=4096,
                vcpus=1,
                environment={
                    "ENV": "",
                    "AWS_BUCKET": "covariate-ingest-data",
                    "STAC_API": "https://discovery-cosmos.azurewebsites.net/stac/dev/addItem"
                },
                privileged=False,
            ),
        )

        events.Rule(
            self,
            'npp-ingest-trigger',
            description='Trigger for sample ingest',
            schedule=events.Schedule.cron(minute="0", hour="4"), # Every day at 4am
            targets=[
                targets.BatchJob(
                    job_queue=job_queue,
                    job_definition=npp_job,
                )
            ],
            enabled=False
        )