from pulumi_aws import ec2


def create_default_route(
    resource_name,
    default_route_table_id=None,
    gateway_id=None,
    tags=None,
    opts=None,
    cidr_block: str = "0.0.0.0/0",  # 기본값 설정
):

    tags_with_name = (tags or {}).copy()
    tags_with_name["Name"] = resource_name

    # CIDR block과 gateway_id를 사용하여 routes 리스트 구성
    routes = [
        ec2.DefaultRouteTableRouteArgs(cidr_block=cidr_block, gateway_id=gateway_id)
    ]

    # 기본 라우트 테이블 생성
    default_route_table = ec2.DefaultRouteTable(
        resource_name,
        default_route_table_id=default_route_table_id,
        routes=routes,
        tags=tags_with_name,
        opts=opts,
    )

    return default_route_table


def create_route_table(resource_name, vpc_id, tags):

    tags_with_name = (tags or {}).copy()
    tags_with_name["Name"] = resource_name

    route_table = ec2.RouteTable(resource_name, vpc_id=vpc_id, tags=tags_with_name)
    return route_table


def associate_subnet_route_table(
    association_name, route_table_id, subnet_id, opts=None
):

    association = ec2.RouteTableAssociation(
        association_name,
        route_table_id=route_table_id,
        subnet_id=subnet_id,
        opts=opts,  # ResourceOptions 인스턴스를 생성자에 전달
    )
    return association


def add_route_to_route_table(
    resource_name,
    route_table_id,
    destination_cidr_block="0.0.0.0/0",
    nat_gateway_id=None,
):
    """
    특정 라우트 테이블에 라우트를 추가하는 함수
    """
    route = ec2.Route(
        resource_name,
        route_table_id=route_table_id,
        destination_cidr_block=destination_cidr_block,
        nat_gateway_id=nat_gateway_id,
    )
    return route
