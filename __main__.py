"""An AWS Python Pulumi program"""

import pulumi
from vpc import create_vpc
from subnet import create_subnet
from security_group import create_security_group, create_security_group_rule
from nat import create_elastic_ip, create_nat_gateway
from route_table import (
    create_default_route,
    create_route_table,
    associate_subnet_route_table,
    add_route_to_route_table,
)
from igw import create_internet_gateway, attach_igw_to_vpc
from vpce import (
    create_interface_vpce,
    create_gateway_vpce,
    attach_vpc_endpoint_policy,
)


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

######## Create Nat Gateway ########
# Create Elastic IP
nat_eip = create_elastic_ip(f"{project}-nat-eip", tags)
# Create Nat Gateway
nat_gateway_a = create_nat_gateway(
    f"{project}-nat-gateway-a",
    subnet_id=subnet_public_ingress_a.id,
    eip_allocation_id=nat_eip.id,
    tags=tags,
)


######## Create Routetable ########
# 라우트 테이블 생성 및 서브넷 연결: app
route_app = create_route_table(
    f"{project}-route-app", vpc.id, {**tags, "Name": f"{project}-route-app"}
)
route_app_association_a = associate_subnet_route_table(
    f"{project}-route-app-association-a", route_app.id, subnet_private_app_a.id
)
route_app_association_c = associate_subnet_route_table(
    f"{project}-route-app-association-c", route_app.id, subnet_private_app_c.id
)
route_app_route_nat = add_route_to_route_table(
    f"{project}-route-app-add-route-nat",
    route_app.id,
    destination_cidr_block="0.0.0.0/0",
    nat_gateway_id=nat_gateway_a.id,
)

######## Create Internet Gateway ########
# 인터넷 게이트웨이 생성 및 VPC에 연결
igw = create_internet_gateway(f"{project}-igw", tags)
vpcgw_attachment = attach_igw_to_vpc(f"{project}-vpcgw-attachment", vpc.id, igw.id)

# 라우트 테이블 생성 및 서브넷 연결: ingress
route_ingress = create_route_table(
    f"{project}-route-ingress",
    vpc_id=vpc.id,
    tags={**tags, "Name": f"{project}-route-ingress"},
)
route_ingress_association_a = associate_subnet_route_table(
    f"{project}-route-ingress-association-a",
    route_ingress.id,
    subnet_id=subnet_public_ingress_a.id,
)
route_ingress_association_c = associate_subnet_route_table(
    f"{project}-route-ingress-association-c",
    route_ingress.id,
    subnet_public_ingress_c.id,
)

# 기본 라우트 설정
route_default = create_default_route(
    f"{project}-route-default",
    default_route_table_id=route_ingress.id,
    cidr_block="0.0.0.0/0",
    gateway_id=igw.id,
    tags=tags,
)

######## Create VPC Endpoints ########
# Interface VPCE 생성
vpce_interface_ecr_api = create_interface_vpce(
    f"{project}-ecr-api-vpce",
    service_name="com.amazonaws.ap-northeast-2.ecr.api",
    vpc_id=vpc.id,
    subnet_ids=[subnet_private_egress_a.id, subnet_private_egress_c.id],
    security_group_id=security_group_vpce.id,
    tags=tags,
)
vpce_interface_ecr_api_policy = attach_vpc_endpoint_policy(
    f"{project}-ecr-api-vpce-policy",
    vpce_interface_ecr_api.id,
    policy={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "ecr:*",
                "Resource": "*",
            }
        ],
    },
    tags=tags,
)
vpce_interface_ecr_dkr = create_interface_vpce(
    f"{project}-ecr-dkr-vpce",
    service_name="com.amazonaws.ap-northeast-2.ecr.dkr",
    vpc_id=vpc.id,
    subnet_ids=[subnet_private_egress_a.id, subnet_private_egress_c.id],
    security_group_id=security_group_vpce.id,
    tags=tags,
)
vpce_interface_ecr_dkr_policy = attach_vpc_endpoint_policy(
    f"{project}-ecr-dkr-vpce-policy",
    vpce_interface_ecr_dkr.id,
    policy={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "ecr:*",
                "Resource": "*",
            }
        ],
    },
    tags=tags,
)

# Gateway VPCE 생성
vpce_s3_gateway = create_gateway_vpce(
    f"{project}-s3-vpce",
    service_name="com.amazonaws.ap-northeast-2.s3",
    vpc_id=vpc.id,
    route_table_ids=[route_app.id],
    tags=tags,
)
vpce_s3_gateway_policy = attach_vpc_endpoint_policy(
    f"{project}-s3-vpce-policy",
    vpce_s3_gateway.id,
    policy={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": "*",
            }
        ],
    },
    tags=tags,
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
pulumi.export(
    "sg_frontend_from_sg_ingress_rule_id", sg_frontend_from_sg_ingress_rule.id
)
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
    "sg_internal_lb_from_sg_management_rule_id",
    sg_internal_lb_from_sg_management_rule.id,
)
pulumi.export("sg_vpce_from_sg_backend_rule_id", sg_vpce_from_sg_backend_rule.id)
pulumi.export("sg_vpce_from_sg_frontend_rule_id", sg_vpce_from_sg_frontend_rule.id)
pulumi.export("sg_vpce_from_sg_management_rule_id", sg_vpce_from_sg_management_rule.id)
# nat gateway
pulumi.export("nat_gateway_a_id", nat_gateway_a.id)
# route table
pulumi.export("route_app_id", route_app.id)
pulumi.export("route_ingress_id", route_ingress.id)
pulumi.export("route_default_id", route_default.id)
# vpc endpoint
pulumi.export("vpce_interface_ecr_api_id", vpce_interface_ecr_api.id)
pulumi.export("vpce_interface_ecr_dkr_id", vpce_interface_ecr_dkr.id)
pulumi.export("vpce_s3_gateway_id", vpce_s3_gateway.id)
# vpc endpoint policy
pulumi.export("vpce_interface_ecr_api_policy_id", vpce_interface_ecr_api_policy.id)
pulumi.export("vpce_interface_ecr_dkr_policy_id", vpce_interface_ecr_dkr_policy.id)
pulumi.export("vpce_s3_gateway_policy_id", vpce_s3_gateway_policy.id)
