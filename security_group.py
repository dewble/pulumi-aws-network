from pulumi_aws import ec2


def create_security_group(
    resource_name,
    vpc_id,
    ingress=None,
    egress=None,
    description=None,
    tags=None,
    opts=None,
):
    # tags가 None일 경우 빈 딕셔너리를 사용
    tags_with_name = (tags or {}).copy()
    tags_with_name["Name"] = resource_name

    # SecurityGroup 리소스 생성
    security_group = ec2.SecurityGroup(
        resource_name,
        vpc_id=vpc_id,
        description=description,
        ingress=ingress or [],  # 간결한 None 체크
        egress=egress or [],  # 간결한 None 체크
        tags=tags_with_name,
        opts=opts,  # 사용자 정의 opts를 명시적으로 전달
    )

    return security_group


# 보안 그룹 간의 인그레스 규칙을 설정하는 방법
def create_security_group_rule(
    resource_name,
    security_group_id,
    source_security_group_id,
    description,
    from_port,
    to_port,
    protocol,
    type,
    opts=None,
):

    security_group_rule = ec2.SecurityGroupRule(
        resource_name,
        description=description,
        from_port=from_port,
        to_port=to_port,
        protocol=protocol,
        security_group_id=security_group_id,
        source_security_group_id=source_security_group_id,
        type=type,
        opts=opts,  # 사용자 정의 opts를 명시적으로 전달
    )

    return security_group_rule
