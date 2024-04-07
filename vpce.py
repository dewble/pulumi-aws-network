from pulumi_aws import ec2
import json


def create_interface_vpce(
    resource_name, service_name, vpc_id, subnet_ids, security_group_id, tags=None
):
    """
    인터페이스형 VPC 엔드포인트 생성 함수
    """
    tags_with_name = tags.copy()
    tags_with_name["Name"] = resource_name

    vpce = ec2.VpcEndpoint(
        resource_name,
        vpc_id=vpc_id,
        service_name=service_name,
        vpc_endpoint_type="Interface",
        subnet_ids=subnet_ids,
        security_group_ids=[security_group_id],
        private_dns_enabled=True,
        tags=tags_with_name,
    )
    return vpce


def create_gateway_vpce(
    resource_name, service_name, vpc_id, route_table_ids, tags=None
):
    """
    게이트웨이형 VPC 엔드포인트 생성 함수
    """
    tags_with_name = tags.copy()
    tags_with_name["Name"] = resource_name
    vpce = ec2.VpcEndpoint(
        resource_name,
        vpc_id=vpc_id,
        service_name=service_name,
        vpc_endpoint_type="Gateway",
        route_table_ids=route_table_ids,
        tags=tags_with_name,
    )
    return vpce


def attach_vpc_endpoint_policy(resource_name, vpc_endpoint_id, policy, tags=None):
    """
    VPC 엔드포인트 정책 적용 함수
    """
    tags_with_name = tags.copy()
    tags_with_name["Name"] = resource_name
    endpoint_policy = ec2.VpcEndpointPolicy(
        resource_name=resource_name,
        vpc_endpoint_id=vpc_endpoint_id,
        policy=json.dumps(policy),
    )
    tags = tags_with_name
    return endpoint_policy
