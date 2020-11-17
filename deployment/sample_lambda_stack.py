from aws_cdk import (
    core,
    aws_lambda as lambdas
)


class SampleLambdaIngestStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)


        lambdas.Function(
            self,
            'sample-ingest-function',
            # function_name=function_name,
            code=lambdas.Code.from_asset(f'./functions/sample_ingest'), # If no dependencies.
            runtime=lambdas.Runtime.PYTHON_3_7,
            handler=f'main.lambda_handler',
            # role=self.function_role,
            timeout=core.Duration.seconds(900),
            memory_size=1024,
            environment={
                "gbdx_token_key": "tdg-pipeline-gbdx-token"
            },
            # layers=[]
        )