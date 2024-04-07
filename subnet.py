from pulumi_aws import ec2, get_availability_zones


def create_subnet(
    resource_name,
    cidr_block,
    vpc_id,
    availability_zone_index,
    map_public_ip_on_launch,
    tags,
):

    tags_with_name = tags.copy()
    tags_with_name["Name"] = resource_name

    azs = get_availability_zones()
    subnet = ec2.Subnet(
        resource_name,
        cidr_block=cidr_block,
        vpc_id=vpc_id,
        availability_zone=azs.names[availability_zone_index],
        map_public_ip_on_launch=map_public_ip_on_launch,
        tags=tags_with_name,
    )
    return subnet
