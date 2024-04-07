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

######## Create Security Groups ########
security_group_ingress = create_security_group(
    resource_name=f"{project}-security-group-ingress",
    vpc_id=vpc.id,
    tags=tags,
    **config.require_object(
        "security_group_ingress"
    ),  # **security_group_ingress_config,
)

security_group_db = create_security_group(
    resource_name=f"{project}-security-group-db",
    vpc_id=vpc.id,
    tags=tags,
    **config.require_object("security_group_db"),  # **security_group_db_config,
)

security_group_management = create_security_group(
    resource_name=f"{project}-security-group-management",
    vpc_id=vpc.id,
    tags=tags,
    **config.require_object(
        "security_group_management"
    ),  # **security_group_management_config,
)

security_group_frontend = create_security_group(
    resource_name=f"{project}-security-group-frontend",
    vpc_id=vpc.id,
    tags=tags,
    **config.require_object(
        "security_group_frontend"
    ),  # **security_group_frontend_config,
)

security_group_backend = create_security_group(
    resource_name=f"{project}-security-group-backend",
    vpc_id=vpc.id,
    tags=tags,
    **config.require_object(
        "security_group_backend"
    ),  # **security_group_backend_config,
)

security_group_internal_lb = create_security_group(
    resource_name=f"{project}-security-group-internal-lb",
    vpc_id=vpc.id,
    tags=tags,
    **config.require_object(
        "security_group_internal_lb"
    ),  # **security_group_internal_lb_config,
)

security_group_vpce = create_security_group(
    resource_name=f"{project}-security-group-vpce",
    vpc_id=vpc.id,
    tags=tags,
    **config.require_object("security_group_vpce"),  # **security_group_vpce_config,
)

# Create Security Group Rules, 보안 그룹 간의 인그레스 규칙 설정
sg_frontend_from_sg_ingress_rule = create_security_group_rule(
    resource_name=f"{project}-sg-frontend-from-sg-ingress",
    security_group_id=security_group_frontend.id,
    source_security_group_id=security_group_ingress.id,
    description="HTTP for Ingress",
    from_port=80,
    to_port=80,
    protocol="tcp",
    type="ingress",
)

sg_internal_lb_from_sg_front_rule = create_security_group_rule(
    resource_name=f"{project}-sg-internal-lb-from-sg-front",
    security_group_id=security_group_internal_lb.id,
    source_security_group_id=security_group_frontend.id,
    description="HTTP for front container",
    from_port=80,
    to_port=80,
    protocol="tcp",
    type="ingress",
)

sg_backend_from_sg_internal_lb_rule = create_security_group_rule(
    resource_name=f"{project}-sg-backend-from-sg-internal_lb",
    security_group_id=security_group_backend.id,
    source_security_group_id=security_group_internal_lb.id,
    description="HTTP for internal lb",
    from_port=80,
    to_port=80,
    protocol="tcp",
    type="ingress",
)

sg_db_from_sg_backend_rule = create_security_group_rule(
    resource_name=f"{project}-sg-db-from-sg-backend",
    security_group_id=security_group_db.id,
    source_security_group_id=security_group_backend.id,
    description="MySQL protocol from backend App",
    from_port=3306,
    to_port=3306,
    protocol="tcp",
    type="ingress",
)

sg_db_from_sg_frontend_rule = create_security_group_rule(
    resource_name=f"{project}-sg-db-from-sg-frontend",
    security_group_id=security_group_db.id,
    source_security_group_id=security_group_frontend.id,
    description="MySQL protocol from frontend App",
    from_port=3306,
    to_port=3306,
    protocol="tcp",
    type="ingress",
)

sg_db_from_sg_management_rule = create_security_group_rule(
    resource_name=f"{project}-sg-db-from-sg-management",
    security_group_id=security_group_db.id,
    source_security_group_id=security_group_management.id,
    description="MySQL protocol from management server",
    from_port=3306,
    to_port=3306,
    protocol="tcp",
    type="ingress",
)

sg_internal_lb_from_sg_management_rule = create_security_group_rule(
    resource_name=f"{project}-sg-internal-lb-from-sg-management",
    security_group_id=security_group_internal_lb.id,
    source_security_group_id=security_group_management.id,
    description="HTTP for management server",
    from_port=80,
    to_port=80,
    protocol="tcp",
    type="ingress",
)

sg_vpce_from_sg_backend_rule = create_security_group_rule(
    resource_name=f"{project}-sg-vpce-from-sg-backend",
    security_group_id=security_group_vpce.id,
    source_security_group_id=security_group_backend.id,
    description="HTTPS for backend App",
    from_port=443,
    to_port=443,
    protocol="tcp",
    type="ingress",
)

sg_vpce_from_sg_frontend_rule = create_security_group_rule(
    resource_name=f"{project}-sg-vpce-from-sg-frontend",
    security_group_id=security_group_vpce.id,
    source_security_group_id=security_group_frontend.id,
    description="HTTPS for frontend App",
    from_port=443,
    to_port=443,
    protocol="tcp",
    type="ingress",
)

sg_vpce_from_sg_management_rule = create_security_group_rule(
    resource_name=f"{project}-sg-vpce-from-sg-management",
    security_group_id=security_group_vpce.id,
    source_security_group_id=security_group_management.id,
    description="HTTPS for management server",
    from_port=443,
    to_port=443,
    protocol="tcp",
    type="ingress",
)

######## Export the name of the bucket ########
# vpc
pulumi.export("vpc_id", vpc.id)
# subnet
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
# security group
pulumi.export("security_group_ingress_id", security_group_ingress.id)
pulumi.export("security_group_db_id", security_group_db.id)
pulumi.export("security_group_management_id", security_group_management.id)
pulumi.export("security_group_frontend_id", security_group_frontend.id)
pulumi.export("security_group_backend_id", security_group_backend.id)
pulumi.export("security_group_internal_lb_id", security_group_internal_lb.id)
pulumi.export("security_group_vpce_id", security_group_vpce.id)
# security group rule
pulumi.export("sg_frontend_from_sg_ingress_rule_id", sg_frontend_from_sg_ingress_rule.id)
pulumi.export(
    "sg_internal_lb_from_sg_front_rule_id", sg_internal_lb_from_sg_front_rule.id
)
pulumi.export(
    "sg_backend_from_sg_internal_lb_rule_id", sg_backend_from_sg_internal_lb_rule.id
)
pulumi.export("sg_db_from_sg_backend_rule_id", sg_db_from_sg_backend_rule.id)
pulumi.export("sg_db_from_sg_frontend_rule_id", sg_db_from_sg_frontend_rule.id)
pulumi.export("sg_db_from_sg_management_rule_id", sg_db_from_sg_management_rule.id)
pulumi.export(
    "sg_internal_lb_from_sg_management_rule_id", sg_internal_lb_from_sg_management_rule.id
)
pulumi.export("sg_vpce_from_sg_backend_rule_id", sg_vpce_from_sg_backend_rule.id)
pulumi.export("sg_vpce_from_sg_frontend_rule_id", sg_vpce_from_sg_frontend_rule.id)
pulumi.export(
    "sg_vpce_from_sg_management_rule_id", sg_vpce_from_sg_management_rule.id
)

