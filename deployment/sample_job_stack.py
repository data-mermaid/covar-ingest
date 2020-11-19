from aws_cdk import (
    core,
    aws_batch as batch,
    aws_events as events,
    aws_events_targets as targets
)


class SampleJobIngestStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # TODO Add setup for running a docker image in Fargate.
        # Will need a seperate stack for Fargate, and VPC.
        pass
        # batch.JobDefinition(
        #     self,
        #     job_name,
        #     # Use this so the name is predictable in other classes.
        #     job_definition_name=job_name,
        #     container=batch.JobDefinitionContainer(
        #         # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_batch/JobDefinitionContainer.html
        #         image=ecs.ContainerImage.from_asset(
        #             "./jobs/car-detection/",
        #             # build_args=None,
        #             # file=None,
        #             # repository_name=None,
        #             # target=None,
        #             # extra_hash=None,
        #             # exclude=None,
        #             # follow=None
        #         ),
        #         job_role=self.job_role,
        #         memory_limit_mib=16384,
        #         vcpus=2,
        #         # gpu_count=1,
        #         command=['python', '/src/command.py', 'Ref::inputurl'],
        #         environment={
        #             'gbdx_token_key': 'tdg-pipeline-gbdx-token',
        #             'AWS_DEFAULT_REGION': 'us-east-1',
        #             'AWS_REGION': 'us-east-1',
        #         },
        #         privileged=False,
        #         # volumes=[], # List of aws_cdk.aws_ecs.Volume
        #         # mount_points=[], # List of aws_cdk.aws_ecs.MountPoint
        #     ),
        #     # retry_attempts=3,
        #     # parameters={'param1': "value1"},
        #     # timeout=, # Object aws_cdk.core.Duration
        #     # node_props= # Object aws_cdk.aws_batch.IMultiNodeProps
        # )
