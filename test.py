import boto3

try:
    # s3 클라이언트 생성
    s3 = boto3.resource(
        service_name="s3",
        region_name="ap-northeast-2",
        aws_access_key_id="AKIATNMX4SNIVSLVLHGA",
        aws_secret_access_key="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",
    )
except Exception as e:
    print(e)
else:
    print("connect success")