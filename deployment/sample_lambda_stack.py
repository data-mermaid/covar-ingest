from aws_cdk import (
    core,
    aws_lambda as lambdas,
    aws_events as events,
    aws_events_targets as targets
)


class SampleLambdaIngestStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ingest_func = lambdas.Function(
            self,
            'sample-ingest-function',
            # function_name=function_name,
            code=lambdas.Code.from_asset(f'./functions/sample_ingest_function'), # If no dependencies.
            runtime=lambdas.Runtime.PYTHON_3_7,
            handler=f'main.lambda_handler',
            # role=self.function_role,
            timeout=core.Duration.seconds(900),
            memory_size=1024,
            environment={
                "key": "value"
            },
            # layers=[]
        )

        events.Rule(
            self,
            'ingest-trigger-sample',
            description='Trigger for sample ingest',
            schedule=events.Schedule.cron(minute="0", hour="4"), # Every day at 4am
            targets=[
                targets.LambdaFunction(handler=ingest_func)
            ]
        )
