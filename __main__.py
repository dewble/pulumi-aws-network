"""An AWS Python Pulumi program"""

import pulumi
from vpc import create_vpc


######## Pulumi 구성 시스템을 사용하여 구성 값을 가져옴 ########
config = pulumi.Config()
vpc_cidr_block = config.require("vpc_cidr_block")
# tags
tags = config.require_object("tags")
## project tags 가져오기
project = tags["Project"]


######## Create VPC ########
vpc = create_vpc(f"{project}-vpc", vpc_cidr_block, tags)

# Export the name of the bucket
pulumi.export("vpc_id", vpc.id)
