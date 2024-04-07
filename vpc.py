from pulumi_aws import ec2


def create_vpc(resource_name, cidr_block, tags):

    # tags가 None이면 빈 딕셔너리를 사용하도록 수정
    tags_with_name = (tags or {}).copy()
    tags_with_name["Name"] = resource_name

    vpc = ec2.Vpc(
        resource_name=resource_name,
        cidr_block=cidr_block,
        enable_dns_hostnames=True,
        enable_dns_support=True,
        instance_tenancy="default",
        tags=tags_with_name,
    )
    return vpc
