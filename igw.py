from pulumi_aws import ec2


def create_internet_gateway(resource_name, tags=None):

    tags_with_name = tags.copy()
    tags_with_name["Name"] = resource_name

    igw = ec2.InternetGateway(resource_name, tags=tags_with_name)
    return igw


def attach_igw_to_vpc(resource_name, vpc_id, igw_id):
    attachment = ec2.InternetGatewayAttachment(
        resource_name,
        vpc_id=vpc_id,
        internet_gateway_id=igw_id,
    )
    return attachment
