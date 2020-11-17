from aws_cdk import (
    core,
)


class SampleJobIngestStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # TODO Add setup for running a docker image in Fargate.
        # Will need a seperate stack for Fargate, and VPC.
