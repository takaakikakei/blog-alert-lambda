from mypy_boto3_lambda.client import LambdaClient


class LambdaService:
    def __init__(self, lambda_client: LambdaClient):
        self._lambda_client = lambda_client

    def describe_deployed_lambda(self):
        # refs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Paginator.ListFunctions
        paginator = self._lambda_client.get_paginator("list_functions")
        lambda_names = []
        for page in paginator.paginate():
            for func_info in page["Functions"]:
                lambda_names.append(func_info["FunctionName"])
        return {"lambda_names": lambda_names}
