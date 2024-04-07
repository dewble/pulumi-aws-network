from pulumi_aws import ec2


def create_elastic_ip(resource_name, tags=None):
    tags_with_name = tags.copy()
    tags_with_name["Name"] = resource_name

    eip = ec2.Eip(resource_name, tags=tags_with_name)
    return eip


def create_nat_gateway(resource_name, subnet_id, eip_allocation_id, tags=None):
    tags_with_name = tags.copy()
    tags_with_name["Name"] = resource_name

    nat_gateway = ec2.NatGateway(
        resource_name,
        subnet_id=subnet_id,
        allocation_id=eip_allocation_id,
        tags=tags_with_name,
    )
    return nat_gateway
