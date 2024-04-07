"""An AWS Python Pulumi program"""

import pulumi
from vpc import create_vpc
from subnet import create_subnet
from security_group import create_security_group, create_security_group_rule


######## Pulumi 구성 시스템을 사용하여 구성 값을 가져옴 ########
config = pulumi.Config()
# tags
tags = config.require_object("tags")
## project tags 가져오기
project = tags["Project"]
# vpc
vpc_cidr_block = config.require("vpc_cidr_block")
# subnets
subnet_app_cidr_blocks = config.require_object("subnet_app_cidr_blocks")
subnet_db_cidr_blocks = config.require_object("subnet_db_cidr_blocks")
subnet_public_ingress_cidr_blocks = config.require_object(
    "subnet_public_ingress_cidr_blocks"
)
subnet_public_management_cidr_blocks = config.require_object(
    "subnet_public_management_cidr_blocks"
)
subnet_private_egress_cidr_blocks = config.require_object(
    "subnet_private_egress_cidr_blocks"
)


######## Create VPC ########
vpc = create_vpc(f"{project}-vpc", vpc_cidr_block, tags)

######## Create Subnets ########
# Create Subnets: app
subnet_private_app_a = create_subnet(
    f"{project}-subnet-private-app-a",
    subnet_app_cidr_blocks[
        0
    ],  # **config.require_object("subnet_app_cidr_blocks") #subnet_app_cidr_blocks[0]
    vpc.id,
    0,  # AZ 인덱스
    False,  # map_public_ip_on_launch
    {**tags, "Type": "Isolated"},
)
subnet_private_app_c = create_subnet(
    f"{project}-subnet-private-app-c",
    subnet_app_cidr_blocks[1],
    vpc.id,
    2,  # AZ 인덱스
    False,  # map_public_ip_on_launch
    {**tags, "Type": "Isolated"},
)

# Create Subnets: db
subnet_private_db_a = create_subnet(
    f"{project}-subnet-private-db-a",
    subnet_db_cidr_blocks[0],
    vpc.id,
    0,  # AZ 인덱스
    False,  # map_public_ip_on_launch
    {**tags, "Type": "Isolated"},
)
subnet_private_db_c = create_subnet(
    f"{project}-subnet-private-db-c",
    subnet_db_cidr_blocks[1],
    vpc.id,
    2,  # AZ 인덱스
    False,  # map_public_ip_on_launch
    {**tags, "Type": "Isolated"},
)

# Create Subnets: public ingress
subnet_public_ingress_a = create_subnet(
    f"{project}-subnet-public-ingress-a",
    subnet_public_ingress_cidr_blocks[0],
    vpc.id,
    0,  # AZ 인덱스
    True,  # map_public_ip_on_launch
    {**tags, "Type": "Public"},
)
subnet_public_ingress_c = create_subnet(
    f"{project}-subnet-public-ingress-c",
    subnet_public_ingress_cidr_blocks[1],
    vpc.id,
    2,  # AZ 인덱스
    True,  # map_public_ip_on_launch
    {**tags, "Type": "Public"},
)

# Create Subnets: public management
subnet_public_management_a = create_subnet(
    f"{project}-subnet-public-management-a",
    subnet_public_management_cidr_blocks[0],
    vpc.id,
    0,  # AZ 인덱스
    True,  # map_public_ip_on_launch
    {**tags, "Type": "Public"},
)
subnet_public_management_c = create_subnet(
    f"{project}-subnet-public-management-c",
    subnet_public_management_cidr_blocks[1],
    vpc.id,
    2,  # AZ 인덱스
    True,  # map_public_ip_on_launch
    {**tags, "Type": "Public"},
)

# Create Subnets: private egress
subnet_private_egress_a = create_subnet(
    f"{project}-subnet-private-egress-a",
    subnet_private_egress_cidr_blocks[0],
    vpc.id,
    0,  # AZ 인덱스
    False,  # map_public_ip_on_launch
    {**tags, "Type": "Isolated"},
)
subnet_private_egress_c = create_subnet(
    f"{project}-subnet-private-egress-c",
    subnet_private_egress_cidr_blocks[1],
    vpc.id,
    2,  # AZ 인덱스
    False,  # map_public_ip_on_launch
    {**tags, "Type": "Isolated"},
)

# Export the name of the bucket
## vpc
pulumi.export("vpc_id", vpc.id)
## subnet
pulumi.export("subnet_private_app_a_id", subnet_private_app_a.id)
pulumi.export("subnet_private_app_c_id", subnet_private_app_c.id)
pulumi.export("subnet_private_db_a_id", subnet_private_db_a.id)
pulumi.export("subnet_private_db_c_id", subnet_private_db_c.id)
pulumi.export("subnet_public_ingress_a_id", subnet_public_ingress_a.id)
pulumi.export("subnet_public_ingress_c_id", subnet_public_ingress_c.id)
pulumi.export("subnet_public_management_a_id", subnet_public_management_a.id)
pulumi.export("subnet_public_management_c_id", subnet_public_management_c.id)
pulumi.export("subnet_private_egress_a_id", subnet_private_egress_a.id)
pulumi.export("subnet_private_egress_c_id", subnet_private_egress_c.id)

