from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_batch as batch,
    aws_ecs as ecs,
    aws_s3 as s3,
    aws_iam as iam
)

# TODO Add Fargate?? Or just use Batch?

class BaseInfrastructure(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        cidr_block: str,
        platform_identifier: str = 'covariate-ingest',
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.lambda_function_role_name = f'{platform_identifier}-lambda-function'
        self.node.set_context('lambda_function_role_name', self.lambda_function_role_name)

        self.batch_job_role_name = f'{platform_identifier}-batch-job'
        self.node.set_context('batch_job_role_name', self.batch_job_role_name)

        self.vpc = ec2.Vpc(
            self,
            "vpc",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            flow_logs={
                "default":
                    ec2.FlowLogOptions(
                        destination=ec2.FlowLogDestination.to_cloud_watch_logs()
                    )
            },
            # max_azs=99,  # Means use all AZs
            max_azs=3,
            cidr=cidr_block,
            # configuration will create a subnet for each config, in each AZ.
            # So us-east-1 3 public, and 3 private
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE,
                    name="Private",
                    cidr_mask=20
                )
            ],
            gateway_endpoints={
                "S3":
                    ec2.GatewayVpcEndpointOptions(
                        service=ec2.GatewayVpcEndpointAwsService.S3
                    )
            },
        )
        self.vpc.add_interface_endpoint(
            "EcrDockerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER
        )

        # Public NACL
        self.nacl_public = ec2.NetworkAcl(
            self,
            "nacl_public",
            vpc=self.vpc,
            subnet_selection=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            )
        )
        self.nacl_public.add_entry(
            "in-rule",
            rule_number=95,
            cidr=ec2.AclCidr.any_ipv4(),
            rule_action=ec2.Action.ALLOW,
            direction=ec2.TrafficDirection.INGRESS,
            traffic=ec2.AclTraffic.tcp_port_range(start_port=0, end_port=65535)
        )
        self.nacl_public.add_entry(
            "out-rule",
            rule_number=95,
            cidr=ec2.AclCidr.any_ipv4(),
            rule_action=ec2.Action.ALLOW,
            direction=ec2.TrafficDirection.EGRESS,
            traffic=ec2.AclTraffic.tcp_port_range(start_port=0, end_port=65535)
        )

        # Private NACL
        self.nacl_private = ec2.NetworkAcl(
            self,
            "nacl_private",
            vpc=self.vpc,
            subnet_selection=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE
            )
        )
        self.nacl_private.add_entry(
            "in-rule",
            rule_number=95,
            cidr=ec2.AclCidr.any_ipv4(),
            rule_action=ec2.Action.ALLOW,
            direction=ec2.TrafficDirection.INGRESS,
            traffic=ec2.AclTraffic.tcp_port_range(start_port=0, end_port=65432)
        )
        self.nacl_private.add_entry(
            "out-rule",
            rule_number=95,
            cidr=ec2.AclCidr.any_ipv4(),
            rule_action=ec2.Action.ALLOW,
            direction=ec2.TrafficDirection.EGRESS,
            traffic=ec2.AclTraffic.tcp_port_range(start_port=0, end_port=65432)
        )

        # Add Batch Compute Envs
        cpu_instances = [
            ec2.InstanceType('c5.large'),
            ec2.InstanceType('c5.xlarge'),
            ec2.InstanceType('c5.2xlarge'),
            ec2.InstanceType('c5.4xlarge'),
            ec2.InstanceType('m5.large'),
            ec2.InstanceType('m5.xlarge'),
            ec2.InstanceType('m5.2xlarge'),
            ec2.InstanceType('m5.4xlarge'),
        ]

        self.cpu_on_demand = batch.ComputeEnvironment(
            self,
            'batch-cpu-on-demand',
            managed=True,
            enabled=True,
            compute_resources=batch.ComputeResources(
                vpc=self.vpc,  # Will select only private subnets.
                type=batch.ComputeResourceType.ON_DEMAND,
                allocation_strategy=batch.AllocationStrategy.
                BEST_FIT_PROGRESSIVE,
                minv_cpus=0,
                maxv_cpus=640,
                desiredv_cpus=0,
                instance_types=cpu_instances,
                image=ecs.EcsOptimizedImage.amazon_linux2(
                    hardware_type=ecs.AmiHardwareType.STANDARD
                ),
            ),
        )

        self.cpu_spot = batch.ComputeEnvironment(
            self,
            'batch-cpu-spot',
            managed=True,
            enabled=True,
            compute_resources=batch.ComputeResources(
                vpc=self.vpc,  # Will select only private subnets.
                type=batch.ComputeResourceType.SPOT,
                allocation_strategy=batch.AllocationStrategy.
                SPOT_CAPACITY_OPTIMIZED,
                bid_percentage=80,
                minv_cpus=0,
                maxv_cpus=640,
                desiredv_cpus=0,
                instance_types=cpu_instances,
                image=ecs.EcsOptimizedImage.amazon_linux2(
                    hardware_type=ecs.AmiHardwareType.STANDARD
                ),
            ),
        )

        self.cpu_spot_first = batch.JobQueue(
            self,
            'cpu-spot-first',
            job_queue_name=f'{platform_identifier}-cpu-queue',
            compute_environments=[
                batch.JobQueueComputeEnvironment(
                    compute_environment=self.cpu_spot, order=1
                ),
                batch.JobQueueComputeEnvironment(
                    compute_environment=self.cpu_on_demand, order=2
                ),
            ],
            enabled=True,
            priority=10
        )

        self.lambda_function_role = iam.Role(
            self,
            'lambda-function-role',
            role_name=self.lambda_function_role_name,
            description='',
            assumed_by=iam.ServicePrincipal(service='lambda.amazonaws.com'),
        )
        

        self.batch_job_role = iam.Role(
            self,
            'batch-job-role',
            role_name=self.batch_job_role_name,
            description='',
            assumed_by=iam.ServicePrincipal(service='ecs-tasks.amazonaws.com'),
        )

        self.intermediate_bucket = s3.Bucket(
            self,
            f'{platform_identifier}-data-bucket',
            bucket_name=f'{platform_identifier}-data-dev',
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
        )
        self.intermediate_bucket.grant_read_write(self.lambda_function_role)
        self.intermediate_bucket.grant_read_write(self.batch_job_role)

        cluster = ecs.Cluster(self, "covar-api-cluster", vpc=self.vpc)
